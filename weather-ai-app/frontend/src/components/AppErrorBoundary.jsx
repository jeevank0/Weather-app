import { Component } from 'react';

class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: error instanceof Error ? error.message : 'Unexpected application error',
    };
  }

  componentDidCatch(error, errorInfo) {
    // Keep logs available for development debugging.
    console.error('App render error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="page">
          <section className="container">
            <h2>Something went wrong</h2>
            <p className="error">The page failed to render after your last action.</p>
            <p className="muted">Please refresh and try again.</p>
            {this.state.errorMessage ? <p className="muted">Error: {this.state.errorMessage}</p> : null}
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}

export default AppErrorBoundary;
