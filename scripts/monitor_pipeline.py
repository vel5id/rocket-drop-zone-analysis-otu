#!/usr/bin/env python3
"""
Pipeline monitor with timeout and detailed logging.
Monitors pipeline execution, kills it if it hangs, and shows at which stage it died.
"""
import os
import sys
import time
import signal
import threading
import subprocess
from datetime import datetime
from pathlib import Path

class PipelineMonitor:
    """Monitor pipeline execution with timeout and stage tracking."""
    
    def __init__(self, timeout_seconds=60, log_file=None):
        self.timeout_seconds = timeout_seconds
        self.log_file = log_file
        self.process = None
        self.timed_out = False
        self.start_time = None
        self.current_stage = "Initializing"
        self.stage_start_time = None
        self.output_lines = []
        
    def set_stage(self, stage_name):
        """Update current pipeline stage."""
        if self.stage_start_time is not None:
            stage_duration = time.time() - self.stage_start_time
            self.log(f"Stage '{self.current_stage}' completed in {stage_duration:.2f}s")
        
        self.current_stage = stage_name
        self.stage_start_time = time.time()
        self.log(f"Entering stage: {stage_name}")
    
    def log(self, message):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        print(full_message)
        self.output_lines.append(full_message)
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(full_message + "\n")
    
    def _timeout_handler(self):
        """Handle timeout - kill the process."""
        self.timed_out = True
        self.log(f"TIMEOUT: Pipeline exceeded {self.timeout_seconds}s timeout")
        self.log(f"Current stage when timed out: {self.current_stage}")
        
        if self.process and self.process.poll() is None:
            self.log("Killing pipeline process...")
            
            # Try graceful termination first
            try:
                self.process.terminate()
                time.sleep(2)
                
                # Force kill if still running
                if self.process.poll() is None:
                    self.process.kill()
                    self.log("Process force-killed")
            except Exception as e:
                self.log(f"Error killing process: {e}")
    
    def _output_reader(self, pipe, is_stderr=False):
        """Read output from pipe and detect stage changes."""
        stream_name = "stderr" if is_stderr else "stdout"
        
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    decoded = line.rstrip()
                    
                    # Log the output
                    prefix = f"[{stream_name.upper()}] " if is_stderr else ""
                    self.log(f"{prefix}{decoded}")
                    
                    # Detect stage changes from common patterns
                    lower_line = decoded.lower()
                    
                    if "step 1" in lower_line or "monte carlo" in lower_line:
                        self.set_stage("Monte Carlo Simulation")
                    elif "step 2" in lower_line or "computing ellipse" in lower_line:
                        self.set_stage("Ellipse Computation")
                    elif "step 3" in lower_line or "generating grid" in lower_line:
                        self.set_stage("Grid Generation")
                    elif "step 4" in lower_line or "saving geojson" in lower_line:
                        self.set_stage("GeoJSON Export")
                    elif "step 5" in lower_line or "visualization" in lower_line:
                        self.set_stage("Visualization")
                    elif "step 6" in lower_line or "calculating otu" in lower_line:
                        self.set_stage("OTU Calculation")
                    elif "complete" in lower_line or "pipeline complete" in lower_line:
                        self.set_stage("Completion")
                    elif "converting to geographic" in lower_line:
                        self.set_stage("Coordinate Conversion")
                    elif "fetching ndvi" in lower_line:
                        self.set_stage("NDVI Fetching")
                    elif "fetching soil" in lower_line:
                        self.set_stage("Soil Data Fetching")
                    elif "fetching relief" in lower_line:
                        self.set_stage("Relief Data Fetching")
        except Exception as e:
            self.log(f"Error reading {stream_name}: {e}")
    
    def run(self, command):
        """Run command with monitoring."""
        self.start_time = time.time()
        self.log(f"Starting pipeline: {' '.join(command)}")
        self.log(f"Timeout: {self.timeout_seconds}s")
        
        # Setup process
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start output readers
        stdout_thread = threading.Thread(
            target=self._output_reader,
            args=(self.process.stdout, False)
        )
        stderr_thread = threading.Thread(
            target=self._output_reader,
            args=(self.process.stderr, True)
        )
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Start timeout timer
        timer = threading.Timer(self.timeout_seconds, self._timeout_handler)
        timer.daemon = True
        timer.start()
        
        # Wait for process completion
        try:
            return_code = self.process.wait()
            timer.cancel()  # Cancel timer if process completed
            
            elapsed = time.time() - self.start_time
            
            if self.timed_out:
                self.log(f"Pipeline terminated due to timeout after {elapsed:.2f}s")
                return False, "timeout", self.current_stage
            else:
                self.log(f"Pipeline completed in {elapsed:.2f}s with return code: {return_code}")
                
                if return_code == 0:
                    self.log("SUCCESS: Pipeline completed successfully")
                    return True, "success", self.current_stage
                else:
                    self.log(f"FAILURE: Pipeline exited with code {return_code}")
                    return False, "error", self.current_stage
                    
        except Exception as e:
            self.log(f"Exception waiting for process: {e}")
            return False, "exception", self.current_stage
    
    def generate_report(self):
        """Generate a summary report."""
        if not self.start_time:
            return "No pipeline execution recorded"
        
        elapsed = time.time() - self.start_time
        status = "TIMED OUT" if self.timed_out else "COMPLETED"
        
        report = [
            "=" * 60,
            "PIPELINE EXECUTION REPORT",
            "=" * 60,
            f"Status: {status}",
            f"Total time: {elapsed:.2f}s",
            f"Timeout: {self.timeout_seconds}s",
            f"Final stage: {self.current_stage}",
            "",
            "Last 20 output lines:",
            "-" * 40
        ]
        
        # Add last 20 output lines
        for line in self.output_lines[-20:]:
            report.append(line)
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor pipeline execution with timeout")
    parser.add_argument("command", nargs=argparse.REMAINDER, 
                       help="Command to execute (e.g., python run_pipeline.py --iterations 100)")
    parser.add_argument("--timeout", type=int, default=120,
                       help="Timeout in seconds (default: 120)")
    parser.add_argument("--log", type=str, default="pipeline_monitor.log",
                       help="Log file path (default: pipeline_monitor.log)")
    parser.add_argument("--report", action="store_true",
                       help="Generate detailed report after execution")
    
    args = parser.parse_args()
    
    if not args.command:
        print("Error: No command specified")
        print("Usage: python monitor_pipeline.py python run_pipeline.py --iterations 100")
        sys.exit(1)
    
    # Create monitor
    monitor = PipelineMonitor(timeout_seconds=args.timeout, log_file=args.log)
    
    # Run pipeline
    success, reason, final_stage = monitor.run(args.command)
    
    # Generate report if requested
    if args.report:
        print("\n" + monitor.generate_report())
    
    # Exit with appropriate code
    if success:
        print(f"\n✓ Pipeline completed successfully in stage: {final_stage}")
        sys.exit(0)
    else:
        print(f"\n✗ Pipeline failed: {reason} in stage: {final_stage}")
        sys.exit(1)

if __name__ == "__main__":
    main()