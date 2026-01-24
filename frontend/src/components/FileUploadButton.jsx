import React, { useRef, useState } from 'react';

export default function FileUploadButton({ onFilesSelected, disabled }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = async (files) => {
    if (!files || files.length === 0) return;
    
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      return true;
    });

    if (validFiles.length > 0) {
      // Process files to read content and create previews
      const processedFiles = await Promise.all(validFiles.map(async (file) => {
        const fileData = {
          name: file.name,
          type: file.type,
          size: file.size,
          lastModified: file.lastModified
        };
        
        console.log(`Processing file: ${file.name}, Type: ${file.type}`);

        // Read content for text-based files - Relaxed check
        // If it's not an image, try to read it as text
        if (!file.type.startsWith('image/')) {
          try {
            console.log(`Reading content for ${file.name}...`);
            const text = await file.text();
            fileData.content = text;
            console.log(`Read ${text.length} characters.`);
          } catch (e) {
            console.error(`Failed to read content of ${file.name}`, e);
          }
        }

        // Create preview for images
        if (file.type.startsWith('image/')) {
          fileData.preview = URL.createObjectURL(file);
        }

        return fileData;
      }));
      
      onFilesSelected(processedFiles);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e) => {
    handleFileSelect(e.target.files);
    // Reset input so same file can be selected again
    e.target.value = '';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (!disabled) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,.pdf,.doc,.docx,.txt"
        onChange={handleFileInputChange}
        className="hidden"
      />
      
      <button
        onClick={handleButtonClick}
        disabled={disabled}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`p-2 rounded-lg transition-all duration-200 ${
          disabled 
            ? 'text-slate-300 cursor-not-allowed' 
            : isDragging
            ? 'bg-indigo-100 text-indigo-600 scale-110'
            : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
        }`}
        title="Attach files"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
      </button>
    </>
  );
}
