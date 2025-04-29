import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Clock } from 'lucide-react';

export default function ChatInterface({ documentIds = [] }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      content: input,
      sender: 'user',
      timestamp: formatTimestamp()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      const response = await fetch('/api/qa/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: input,
          document_ids: documentIds,
          max_results: 5
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      // Format source citations
      let sourcesText = '';
      if (data.sources && data.sources.length > 0) {
        sourcesText = '\n\nSources:\n' + data.sources.map((source, index) => {
          const filename = source.filename || 'Document';
          const page = source.page_num ? ` (Page ${source.page_num})` : '';
          return `[${index + 1}] ${filename}${page}`;
        }).join('\n');
      }
      
      const botMessage = {
        id: Date.now() + 1,
        content: data.answer + sourcesText,
        sender: 'bot',
        timestamp: formatTimestamp()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching answer:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        sender: 'bot',
        timestamp: formatTimestamp(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden">
      <div className="bg-gray-100 p-4 border-b">
        <h3 className="font-medium">Document Assistant</h3>
        <p className="text-xs text-gray-600">
          Ask questions about your documents
        </p>
      </div>
      
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 my-12">
            <Bot className="w-12 h-12 mx-auto text-gray-300 mb-2" />
            <p>Ask me any questions about your documents</p>
          </div>
        ) : (
          messages.map(message => (
            <div 
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-3/4 rounded-lg p-3 ${
                  message.sender === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : message.isError 
                      ? 'bg-red-50 text-red-800 border border-red-200' 
                      : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                  {message.sender === 'user' ? (
                    <User className="w-3 h-3" />
                  ) : (
                    <Bot className="w-3 h-3" />
                  )}
                  <span>{message.timestamp}</span>
                </div>
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3 flex items-center gap-2">
              <div className="animate-pulse flex space-x-1">
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                <div className="h-2.5 w-2.5 bg-gray-500 rounded-full"></div>
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
              </div>
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="border-t p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-grow rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white rounded-md px-4 py-2 disabled:bg-blue-300 hover:bg-blue-700 transition-colors"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}