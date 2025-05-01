import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const About = () => {
    return (
        <div>
            <Header />
            <main className="container mx-auto p-4">
                <h2 className="text-2xl font-bold mb-4">About Us</h2>
                <p>
                    The Document Intelligence Suite is designed to help you process and analyze documents
                    efficiently. From OCR to semantic chunking, we provide tools to make your data accessible
                    and actionable.
                </p>
            </main>
            <Footer />
        </div>
    );
};

export default About;