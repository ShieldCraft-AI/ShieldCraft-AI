import React from 'react';
import Layout from '@theme/Layout';
import { loginWithHostedUI } from '@site/src/utils/auth-cognito';
import styles from './login.module.css';

function LoginPage() {
  React.useEffect(() => {
    // Redirect to Cognito Hosted UI for real authentication
    loginWithHostedUI();
  }, []);

  return (
    <Layout title="Login" description="Login to ShieldCraft AI">
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h1>ShieldCraft AI</h1>
          <p>Redirecting to login...</p>
        </div>
      </div>
    </Layout>
  );
}

export default LoginPage;
