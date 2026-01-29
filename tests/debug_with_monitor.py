#!/usr/bin/env python3
"""
Debug script with progress monitoring and timeout killing.
"""
import sys
import time
import threading
import subprocess
import os
from pathlib import Path
import signal

class PipelineMonitor:
    """Monitor pipeline progress and kill if stuck."""
    
    def __init__(self, timeout_seconds=60, check_interval=2):
        self.timeout = timeout_seconds
        self.check_interval = check_interval
        self.running = True
        self.process = None
        self.last_activity = time.time()
        self.stage = "Starting"
        self.output_lines = []
        
    def update_stage(self, stage):
        """Update current stage."""
        self.stage = stage
        self.last_activity = time.time()
        print(f"[MONITOR] Stage: {stage} (elapsed: {time.time() - self.start_time:.1f}s)")
    
    def read_output(self, pipe):
        """Read output from pipe and detect stages."""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    line = line.rstrip()
                    self.output_lines.append(line)
                    print(f"[OUTPUT] {line}")
                    
                    # Detect stages from output
                    if "[1/5]" in line or "Monte Carlo" in line:
                        self.update_stage("Monte Carlo Simulation")
                    elif "[2/5]" in line or "Computing Ellipses" in line:
                        self.update_stage("Computing Ellipses")
                    elif "[3/5]" in line or "Creating Polygons" in line:
                        self.update_stage("Creating Polygons")
                    elif "[4/5]" in line or "Generating Grid" in line:
                        self.update_stage("Generating Grid")
                    elif "[5/5]" in line or "Calculating OTU" in line:
                        self.update_stage("Calculating OTU")
                    elif "COMPLETE" in line or "PIPELINE COMPLETE" in line:
                        self.update_stage("Complete")
                    
                    self.last_activity = time.time()
        except Exception as e:
            print(f"[MONITOR] Error reading output: {e}")
    
    def monitor_timeout(self):
        """Monitor for timeout and kill process if stuck."""
        print(f"[MONITOR] Starting timeout monitor ({self.timeout}s timeout)")
        
        while self.running:
            time.sleep(self.check_interval)
            
            if not self.process:
                continue
                
            elapsed_inactive = time.time() - self.last_activity
            total_elapsed = time.time() - self.start_time
            
            # Check if process is still alive
            if self.process.poll() is not None:
                print(f"[MONITOR] Process finished with code {self.process.returncode}")
                self.running = False
                break
            
            # Check for timeout
            if total_elapsed > self.timeout:
                print(f"[MONITOR] TIMEOUT! Process running for {total_elapsed:.1f}s > {self.timeout}s")
                print(f"[MONITOR] Last stage: {self.stage}")
                print(f"[MONITOR] Last activity: {elapsed_inactive:.1f}s ago")
                self.kill_process()
                break
            
            # Check for stuck stage (no activity for 30s)
            if elapsed_inactive > 30:
                print(f"[MONITOR] WARNING: No activity for {elapsed_inactive:.1f}s in stage: {self.stage}")
                # Don't kill yet, just warn
    
    def kill_process(self):
        """Kill the monitored process."""
        if self.process and self.process.poll() is None:
            print(f"[MONITOR] Killing process PID {self.process.pid}")
            
            # Try graceful termination first
            try:
                if os.name == 'nt':  # Windows
                    self.process.terminate()
                else:
                    os.kill(self.process.pid, signal.SIGTERM)
                
                # Wait a bit
                time.sleep(2)
                
                # Force kill if still alive
                if self.process.poll() is None:
                    print("[MONITOR] Force killing process")
                    if os.name == 'nt':
                        self.process.kill()
                    else:
                        os.kill(self.process.pid, signal.SIGKILL)
            except Exception as e:
                print(f"[MONITOR] Error killing process: {e}")
            
            self.running = False
    
    def run_pipeline(self, cmd):
        """Run pipeline with monitoring."""
        print(f"[MONITOR] Running command: {cmd}")
        print(f"[MONITOR] Timeout: {self.timeout}s")
        
        self.start_time = time.time()
        self.last_activity = self.start_time
        
        try:
            # Start process with pipes for stdout/stderr
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Start output reader thread
            output_thread = threading.Thread(target=self.read_output, args=(self.process.stdout,))
            output_thread.daemon = True
            output_thread.start()
            
            # Start monitor thread
            monitor_thread = threading.Thread(target=self.monitor_timeout)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Wait for process to complete
            while self.running and self.process.poll() is None:
                time.sleep(0.5)
            
            # Give threads time to finish
            time.sleep(1)
            
            # Get final return code
            return_code = self.process.poll()
            
            if return_code == 0:
                print(f"[MONITOR] Process completed successfully in {time.time() - self.start_time:.1f}s")
                return True
            else:
                print(f"[MONITOR] Process failed with code {return_code}")
                # Show last 10 lines of output
                print(f"[MONITOR] Last 10 output lines:")
                for line in self.output_lines[-10:]:
                    print(f"  {line}")
                return False
                
        except Exception as e:
            print(f"[MONITOR] Error running pipeline: {e}")
            return False
        finally:
            self.running = False

def main():
    """Main debug function."""
    print("="*60)
    print("OTU PIPELINE DEBUG WITH MONITOR")
    print("="*60)
    
    # Clean output directory
    output_dir = Path("output/debug_monitor")
    if output_dir.exists():
        import shutil
        try:
            shutil.rmtree(output_dir)
            print(f"[MAIN] Cleaned output directory: {output_dir}")
        except Exception as e:
            print(f"[MAIN] Warning: Could not clean directory: {e}")
    
    # Run pipeline with monitor
    cmd = "venv_311\\Scripts\\python.exe run_otu_pipeline.py --date 2024-09-09 --iterations 5 --mock --no-gpu --output output/debug_monitor"
    
    monitor = PipelineMonitor(timeout_seconds=120)  # 2 minute timeout
    success = monitor.run_pipeline(cmd)
    
    # Check output files
    print("\n" + "="*60)
    print("OUTPUT FILES CHECK")
    print("="*60)
    
    if output_dir.exists():
        files = list(output_dir.rglob("*"))
        if files:
            print(f"Found {len(files)} files in {output_dir}:")
            for f in sorted(files, key=lambda x: x.stat().st_size, reverse=True)[:10]:  # Top 10 by size
                if f.is_file():
                    size_kb = f.stat().st_size / 1024
                    print(f"  {f.relative_to(output_dir)}: {size_kb:.1f} KB")
        else:
            print(f"No files found in {output_dir}")
    else:
        print(f"Output directory {output_dir} does not exist")
    
    # Summary
    print("\n" + "="*60)
    print("DEBUG SUMMARY")
    print("="*60)
    
    if success:
        print("[SUCCESS] Pipeline completed within timeout")
    else:
        print("[FAILURE] Pipeline failed or timed out")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)