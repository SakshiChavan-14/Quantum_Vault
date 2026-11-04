import React from 'react';
import Navbar from '../../components/layout/Navbar';
import Hero from '../../components/common/Hero';
import Features from '../../components/common/Features';
import Footer from '../../components/layout/Footer';

const Landing = () => {
  return (
    <div id="landing-page" className="page">
      <Navbar />
      <Hero />
      <Features />
      <Footer />
    </div>
  );
};

export default Landing;
