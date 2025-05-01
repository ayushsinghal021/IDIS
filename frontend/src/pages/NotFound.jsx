import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const NotFound = () => {
    return (
        <div>
            <Header />
            <main className="container mx-auto p-4 text-center">
                <h2 className="text-2xl font-bold mb-4">404 - Page Not Found</h2>
                <p>The page you are looking for does not exist.</p>
            </main>
            <Footer />
        </div>
    );
};

export default NotFound;