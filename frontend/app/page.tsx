"use client";
import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Veredicto = "CUMPLE" | "CUMPLE PARCIALMENTE" | "NO CUMPLE";

interface ResultadoAPI {
  veredicto: Veredicto;
  porcentaje_estimado: string | number;
  justificacion: string;
}

export default function EvaluadorCACES() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResultadoAPI | null>(null);
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

  // Función para obtener los colores semánticos basados en el veredicto
  const getThemeVars = (veredicto: Veredicto) => {
    switch (veredicto) {
      case "CUMPLE":
        return {
          border: "border-emerald-500",
          bgInfo: "bg-emerald-500/10",
          textInfo: "text-emerald-400",
          shadow: "shadow-emerald-500/20",
          bar: "bg-gradient-to-r from-emerald-400 to-green-500",
        };
      case "CUMPLE PARCIALMENTE":
        return {
          border: "border-amber-500",
          bgInfo: "bg-amber-500/10",
          textInfo: "text-amber-400",
          shadow: "shadow-amber-500/20",
          bar: "bg-gradient-to-r from-amber-400 to-orange-500",
        };
      case "NO CUMPLE":
        return {
          border: "border-rose-500",
          bgInfo: "bg-rose-500/10",
          textInfo: "text-rose-400",
          shadow: "shadow-rose-500/20",
          bar: "bg-gradient-to-r from-rose-500 to-red-600",
        };
      default:
        return {
          border: "border-gray-500",
          bgInfo: "bg-gray-500/10",
          textInfo: "text-gray-400",
          shadow: "shadow-gray-500/20",
          bar: "bg-gray-500",
        };
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] flex items-center justify-center p-6 font-sans text-slate-200 overflow-x-hidden">
      
      {/* Contenedor Flex Dinámico para las columnas */}
      <motion.div 
        layout
        className={`flex flex-col xl:flex-row gap-8 w-full items-stretch justify-center transition-all duration-700 ease-in-out ${result && !loading ? 'max-w-7xl' : 'max-w-3xl'}`}
      >
        
        {/* Columna Izquierda: Zona de Subida y Acción */}
        <motion.div 
          layout
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full flex-1 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-[2rem] p-8 md:p-12 shadow-2xl relative overflow-hidden flex flex-col justify-center"
        >
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 mb-4 tracking-tight">
              Auditor Inteligente
            </h1>
            <p className="text-slate-400 font-medium text-lg">
              Sistema de Evaluación Normativa CACES
            </p>
          </div>

          {/* Zona de Drop & Upload */}
          <div 
            className={`relative border-2 border-dashed rounded-3xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
              ${isDragging ? "border-indigo-500 bg-indigo-500/10 scale-[1.02]" : "border-slate-700 hover:border-indigo-400 hover:bg-slate-800/50"}
              ${file && !loading && !result ? "border-emerald-500/50 bg-emerald-500/5" : ""}
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
            
            <svg className={`w-14 h-14 mb-4 transition-colors duration-300 ${file ? 'text-emerald-400' : 'text-slate-500 group-hover:text-indigo-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            
            {file ? (
              <p className="text-lg font-medium text-emerald-300 truncate max-w-full px-4">{file.name}</p>
            ) : (
              <div className="text-center">
                <p className="text-slate-300 text-lg mb-1">Arrastra tu evidencia PDF aquí</p>
                <p className="text-indigo-400 font-semibold text-sm">o haz clic para explorar tus archivos</p>
              </div>
            )}
          </div>

          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-300 text-sm text-center"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Botón de Acción */}
          <div className="mt-8 flex justify-center">
            <button 
              onClick={procesarDocumento}
              disabled={!file || loading}
              className={`relative overflow-hidden px-10 py-4 rounded-2xl font-bold text-lg tracking-wide transition-all duration-300
                ${!file || loading 
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed" 
                  : "bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)]"
                }
              `}
            >
              {loading ? (
                <span className="flex items-center gap-3">
                  <svg className="animate-spin h-5 w-5 text-white/80" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Evaluando con IA...
                </span>
              ) : "Generar Dictamen Oficial"}
            </button>
          </div>
        </motion.div>

        {/* Columna Derecha: Tarjeta de Resultados */}
        <AnimatePresence mode="wait">
          {result && !loading && (
            <motion.div 
              layout
              initial={{ opacity: 0, x: 50, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 50, scale: 0.95 }}
              transition={{ duration: 0.6, type: "spring", bounce: 0.4 }}
              className={`w-full flex-1 p-8 md:p-12 rounded-[2rem] bg-slate-900/80 backdrop-blur-xl border ${getThemeVars(result.veredicto).border} shadow-2xl ${getThemeVars(result.veredicto).shadow} overflow-hidden relative flex flex-col justify-center`}
            >
              {/* Background Glow */}
              <div className={`absolute top-0 left-0 w-full h-full ${getThemeVars(result.veredicto).bgInfo} opacity-30 pointer-events-none`} />

              <div className="relative z-10 flex flex-col gap-10">
                
                {/* Header de la Tarjeta */}
                <div className="flex flex-row items-center justify-between gap-4">
                  <div className="flex-1 text-left">
                    <h3 className="text-slate-400 uppercase tracking-widest text-xs font-bold mb-2">Dictamen del Auditor</h3>
                    <motion.div 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 }}
                      className={`text-3xl md:text-4xl font-black ${getThemeVars(result.veredicto).textInfo} leading-tight`}
                    >
                      {result.veredicto}
                    </motion.div>
                  </div>
                  
                  {/* Círculo / Badge de Porcentaje */}
                  <motion.div 
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ delay: 0.3, type: "spring", bounce: 0.5 }}
                    className={`shrink-0 w-24 h-24 rounded-full border-[5px] flex items-center justify-center ${getThemeVars(result.veredicto).border} ${getThemeVars(result.veredicto).bgInfo} shadow-inner`}
                  >
                    <div className="text-center">
                      <span className={`text-3xl font-black ${getThemeVars(result.veredicto).textInfo}`}>{result.porcentaje_estimado}</span>
                      <span className={`text-xs block font-bold ${getThemeVars(result.veredicto).textInfo} opacity-80 -mt-1`}>%</span>
                    </div>
                  </motion.div>
                </div>

                {/* Barra de Progreso Animada */}
                <div className="w-full bg-slate-800/80 rounded-full h-4 overflow-hidden shadow-inner border border-slate-700/50">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${result.porcentaje_estimado}%` }}
                    transition={{ duration: 1.2, delay: 0.5, ease: "easeOut" }}
                    className={`h-full rounded-full ${getThemeVars(result.veredicto).bar}`}
                  />
                </div>

                {/* Justificación */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                  className="bg-slate-950/60 p-6 rounded-2xl border border-slate-800 shadow-lg flex flex-col"
                >
                  <h4 className="text-slate-300 font-semibold mb-3 flex items-center gap-2 text-base">
                    <svg className={`w-5 h-5 ${getThemeVars(result.veredicto).textInfo}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Análisis Detallado
                  </h4>
                  <div className="max-h-48 overflow-y-auto pr-2">
                    <p className="text-slate-400 leading-relaxed text-sm md:text-base font-light">
                      {result.justificacion}
                    </p>
                  </div>
                </motion.div>

              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </motion.div>
    </div>
  );
}
