import React from 'react';
import Layout from '@theme/Layout';
import styles from './login.module.css';

function LoginPage() {
  React.useEffect(() => {
    // Header-only login: arriving at /login triggers a simple demo auth and redirects
    try { window.localStorage.setItem('sc-auth', '1'); } catch { }
    if (typeof window !== 'undefined') {
      window.location.replace('/portal');
    }
  }, []);
  return (
    <Layout title="Login" description="Login to ShieldCraft AI">
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h1>ShieldCraft AI</h1>
          <p>Signing you in…</p>
        </div>
      </div>
    </Layout>
  );
}

export default LoginPage;
