import React, { useState } from 'react';
import { Upload, CheckCircle, AlertTriangle, Loader } from 'lucide-react';

export default function DocumentUploader() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  const handleFileChange = (e) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles([...files, ...newFiles]);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      setFiles([...files, ...newFiles]);
    }
  };
  
  const uploadFile = async (file) => {
    setUploadProgress(prev => ({...prev, [file.name]: {status: 'uploading', progress: 0}}));
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('process', 'true');
      formData.append('extract_entities', 'true');
      
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({
            ...prev, 
            [file.name]: {status: 'uploading', progress: percentCompleted}
          }));
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUploadProgress(prev => ({
          ...prev, 
          [file.name]: {status: 'success', progress: 100, documentId: data.document_id}
        }));
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadProgress(prev => ({
        ...prev, 
        [file.name]: {status: 'error', progress: 0, error: error.message}
      }));
    }
  };
  
  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    
    try {
      // Upload files sequentially
      for (const file of files) {
        if (!uploadProgress[file.name] || uploadProgress[file.name].status !== 'success') {
          await uploadFile(file);
        }
      }
    } finally {
      setUploading(false);
    }
  };
  
  const removeFile = (fileName) => {
    setFiles(files.filter(file => file.name !== fileName));
    setUploadProgress(prev => {
      const updated = {...prev};
      delete updated[fileName];
      return updated;
    });
  };
  
  return (
    <div className="w-full max-w-3xl mx-auto">
      <div 
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition-colors"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById('fileInput').click()}
      >
        <input
          id="fileInput"
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          <span className="font-semibold">Click to upload</span> or drag and drop
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          PDF, Word documents, Images
        </p>
      </div>
      
      {files.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-medium">Selected Files</h4>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:bg-blue-300 hover:bg-blue-700 transition-colors"
            >
              {uploading ? 'Uploading...' : 'Upload All'}
            </button>
          </div>
          
          <ul className="space-y-3">
            {files.map((file, index) => (
              <li key={index} className="bg-white p-3 rounded-md shadow-sm flex items-center">
                <div className="flex-grow">
                  <div className="flex justify-between">
                    <p className="text-sm font-medium truncate" title={file.name}>
                      {file.name}
                    </p>
                    <button 
                      onClick={(e) => { e.stopPropagation(); removeFile(file.name); }}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      &times;
                    </button>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                  
                  {uploadProgress[file.name] && (
                    <div className="mt-1">
                      {uploadProgress[file.name].status === 'uploading' && (
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div 
                            className="bg-blue-600 h-2.5 rounded-full"
                            style={{ width: `${uploadProgress[file.name].progress}%` }}  
                          />
                        </div>
                      )}
                      
                      {uploadProgress[file.name].status === 'success' && (
                        <div className="flex items-center text-green-600 text-xs">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          <span>Upload complete</span>
                        </div>
                      )}
                      
                      {uploadProgress[file.name].status === 'error' && (
                        <div className="flex items-center text-red-600 text-xs">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          <span>{uploadProgress[file.name].error || 'Upload failed'}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}