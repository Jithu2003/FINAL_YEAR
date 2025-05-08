import React, { useState } from 'react';
import axios from 'axios';

const ReportDownload = ({ reportText }) => {
  const [language, setLanguage] = useState('ta');

  const handleDownload = async () => {
    try {
      const response = await axios.post('http://localhost:8000/translate-download', {
        text: reportText,
        target_lang: language,
      }, {
        responseType: 'blob', // Important for PDF
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'translated_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("PDF download failed:", error);
    }
  };

  return (
    <div className="p-4">
      <label className="mr-2">Select Language:</label>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="border px-2 py-1 rounded"
      >
        <option value="ta">Tamil</option>
        <option value="hi">Hindi</option>
        <option value="fr">French</option>
        <option value="es">Spanish</option>
      </select>
      <button
        onClick={handleDownload}
        className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Download Translated PDF
      </button>
    </div>
  );
};

export default ReportDownload;
