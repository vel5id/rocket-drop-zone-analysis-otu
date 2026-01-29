import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        // Update state so the next render will show the fallback UI.
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ error, errorInfo });
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    padding: '2rem',
                    backgroundColor: '#050a10',
                    color: '#ef4444',
                    height: '100vh',
                    width: '100vw',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'monospace'
                }}>
                    <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Something went wrong.</h1>
                    <div style={{
                        padding: '1rem',
                        border: '1px solid #ef4444',
                        borderRadius: '0.5rem',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        maxWidth: '80%',
                        overflow: 'auto'
                    }}>
                        <p style={{ fontWeight: 'bold' }}>{this.state.error && this.state.error.toString()}</p>
                        <pre style={{ marginTop: '1rem', fontSize: '0.8rem', whiteSpace: 'pre-wrap' }}>
                            {this.state.errorInfo && this.state.errorInfo.componentStack}
                        </pre>
                    </div>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            marginTop: '2rem',
                            padding: '0.75rem 1.5rem',
                            backgroundColor: '#ef4444',
                            color: 'white',
                            border: 'none',
                            borderRadius: '0.25rem',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            textTransform: 'uppercase'
                        }}
                    >
                        Reload Application
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
