import React from 'react';

const Button = ({ label, onClick, type = 'button', className = '' }) => {
    return (
        <button
            type={type}
            onClick={onClick}
            className={`bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 ${className}`}
        >
            {label}
        </button>
    );
};

export default Button;