import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import FileUpload from '../components/FileUpload';

const Home = () => {
    return (
        <div>
            <Header />
            <main className="container mx-auto p-4">
                <h2 className="text-2xl font-bold mb-4">Welcome to Document Intelligence Suite</h2>
                <p className="mb-4">
                    Upload your documents, ask questions, and export structured data.
                </p>
                <FileUpload />
            </main>
            <Footer />
        </div>
    );
};

export default Home;