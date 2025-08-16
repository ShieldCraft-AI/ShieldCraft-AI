import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './login.module.css';

function LoginPage() {
  return (
    <Layout title="Login" description="Login to ShieldCraft AI">
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h1>ShieldCraft AI</h1>
          <p>Next-Gen Cloud Cybersecurity</p>
          <Link className="button button--primary button--lg" to="/portal">
            Login with SSO
          </Link>
        </div>
      </div>
    </Layout>
  );
}

export default LoginPage;
