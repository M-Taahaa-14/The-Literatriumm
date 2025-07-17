import React from 'react';
import Layout from '../components/Layout';

const HomePage = () => {
  return (
    <Layout>
      <div className="home-page">
        <h1>Welcome to Literatrium</h1>
        <p>Your digital library management system</p>
        {/* TODO: Add featured books, search, categories */}
      </div>
    </Layout>
  );
};

export default HomePage;
