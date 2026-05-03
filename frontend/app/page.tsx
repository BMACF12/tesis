"use client";
import React, { useState, useRef } from "react";

export default function EvaluadorCACES() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ veredicto: string; justificacion: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        setResult(null);
        setError(null);
      } else {
        setError("Por favor, sube únicamente archivos PDF.");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const procesarDocumento = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/evaluar_documento/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error en la respuesta del servidor.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Ocurrió un error al contactar con la IA. Asegúrate de que el backend esté corriendo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#000000] flex items-center justify-center p-6 font-sans text-white">

      {/* Contenedor Principal con efecto Glassmorphism */}
      <div className="w-full max-w-2xl bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.4)] transition-all duration-300">

        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 mb-3 tracking-tight">
            Auditor Inteligente CACES
          </h1>
          <p className="text-gray-400 font-light">Sube tu evidencia en PDF y nuestro modelo RAG evaluará su cumplimiento al instante.</p>
        </div>

        {/* Zona de Drop & Upload */}
        <div
          className={`relative border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
            ${isDragging ? "border-purple-500 bg-purple-500/10 scale-105" : "border-gray-500/50 hover:border-purple-400 hover:bg-white/5"}
            ${file && !loading && !result ? "border-green-500/50 bg-green-500/5" : ""}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileChange}
          />

          <svg className={`w-14 h-14 mb-4 transition-colors duration-300 ${file ? 'text-green-400' : 'text-gray-400 group-hover:text-purple-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>

          {file ? (
            <p className="text-lg font-medium text-green-300 truncate max-w-full px-4">{file.name}</p>
          ) : (
            <p className="text-gray-300 text-lg">Arrastra tu PDF aquí o <span className="text-purple-400 font-semibold">haz clic para explorar</span></p>
          )}
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200 text-sm text-center animate-pulse">
            {error}
          </div>
        )}

        {/* Botón de Acción */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={procesarDocumento}
            disabled={!file || loading}
            className={`relative overflow-hidden px-8 py-3 rounded-full font-bold text-lg tracking-wide transition-all duration-300 transform
              ${!file || loading
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-105 hover:shadow-[0_0_20px_rgba(168,85,247,0.5)] active:scale-95 text-white"
              }
            `}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Auditor IA Analizando...
              </span>
            ) : "Evaluar Evidencia"}
          </button>
        </div>

        {/* Tarjeta de Resultados */}
        {result && !loading && (
          <div className="mt-10 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md animate-fade-in-up">
            <div className="flex flex-col md:flex-row items-center gap-6">

              {/* Veredicto */}
              <div className={`flex items-center justify-center w-28 h-28 shrink-0 rounded-full border-4 shadow-lg
                ${result.veredicto === "SÍ"
                  ? "border-green-500 bg-green-500/10 text-green-400 shadow-green-500/30"
                  : "border-red-500 bg-red-500/10 text-red-400 shadow-red-500/30"
                }
              `}>
                <span className="text-4xl font-black">{result.veredicto}</span>
              </div>

              {/* Justificación */}
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-lg font-semibold text-gray-200 mb-2">Justificación del Modelo:</h3>
                <p className="text-gray-400 leading-relaxed text-sm md:text-base">
                  {result.justificacion}
                </p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
