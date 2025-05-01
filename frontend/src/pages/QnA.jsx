import React, { useState } from 'react';
import { askQuestion } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';

const QnA = () => {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');

    const handleAsk = async () => {
        try {
            const response = await askQuestion(question);
            setAnswer(response.answer);
        } catch (error) {
            setAnswer(`Error: ${error.message}`);
        }
    };

    return (
        <div>
            <Header />
            <main className="container mx-auto p-4">
                <h2 className="text-2xl font-bold mb-4">Interactive Q&A</h2>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question..."
                    className="border p-2 w-full mb-4"
                />
                <button
                    onClick={handleAsk}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                    Ask
                </button>
                {answer && <p className="mt-4">{answer}</p>}
            </main>
            <Footer />
        </div>
    );
};

export default QnA;