"use client";
import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Veredicto = "CUMPLE" | "CUMPLE PARCIALMENTE" | "NO CUMPLE";

interface ResultadoAPI {
  veredicto: Veredicto;
  porcentaje_estimado: string | number;
  justificacion: string;
  indicador_evaluado: string;
}

interface EnqueuedTask {
  task_id: string;
  documento: string;
  status: "EN COLA" | "COMPLETADO" | "ERROR" | "PROCESANDO";
  resultado?: ResultadoAPI;
  error?: string;
}

export default function EvaluadorCACES() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [enqueuedTasks, setEnqueuedTasks] = useState<EnqueuedTask[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Polling para revisar el estado de las tareas
  useEffect(() => {
    const hasPendingTasks = enqueuedTasks.some(
      (t) => t.status === "EN COLA" || t.status === "PROCESANDO"
    );

    if (!hasPendingTasks) return;

    const interval = setInterval(async () => {
      setEnqueuedTasks((currentTasks) => {
        // Hacemos un fetch por cada tarea pendiente
        const checkStatuses = async () => {
          const updated = await Promise.all(
            currentTasks.map(async (t) => {
              if (t.status === "COMPLETADO" || t.status === "ERROR") return t;

              try {
                const res = await fetch(`http://127.0.0.1:8000/status/${t.task_id}`);
                const data = await res.json();
                
                if (data.status === "COMPLETADO") {
                  return { ...t, status: "COMPLETADO", resultado: data.resultado };
                } else if (data.status === "ERROR") {
                  return { ...t, status: "ERROR", error: data.error };
                } else {
                  return { ...t, status: data.status }; // Mantiene EN COLA u otro
                }
              } catch (e) {
                return t; // Falla silenciosa de red temporal
              }
            })
          );
          setEnqueuedTasks(updated as EnqueuedTask[]);
        };

        checkStatuses();
        return currentTasks; 
      });
    }, 3000); // Polling cada 3 segundos

    return () => clearInterval(interval);
  }, [enqueuedTasks]);

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
      const droppedFiles = Array.from(e.dataTransfer.files).filter(f => f.type === "application/pdf");
      if (droppedFiles.length > 0) {
        setFiles(prev => [...prev, ...droppedFiles]);
        setEnqueuedTasks([]);
        setError(null);
      } else {
        setError("Por favor, sube únicamente archivos PDF.");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files).filter(f => f.type === "application/pdf");
      setFiles(prev => [...prev, ...selectedFiles]);
      setEnqueuedTasks([]);
      setError(null);
    }
  };

  const procesarDocumentos = async () => {
    if (files.length === 0) return;

    setLoading(true);
    setError(null);
    setEnqueuedTasks([]);

    try {
      const tasks: EnqueuedTask[] = [];
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://127.0.0.1:8000/evaluar_documento/", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Error al encolar: " + file.name);
        }

        const data = await response.json();
        tasks.push({ task_id: data.task_id, documento: data.documento, status: "EN COLA" });
      }
      setEnqueuedTasks(tasks);
      setFiles([]); // Limpiar cola visual
    } catch (err) {
      setError("Error de conexión. Asegúrate de que el backend FastAPI esté ejecutándose.");
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener los colores semánticos
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
    <div className="min-h-screen bg-[#020617] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] flex flex-col items-center justify-start p-6 font-sans text-slate-200 overflow-x-hidden">
      
      <div className="text-center mt-10 mb-8">
        <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 mb-4 tracking-tight">
          Auditor IA Asíncrono
        </h1>
        <p className="text-slate-400 font-medium text-lg">
          Sistema de Encolamiento Masivo para Evaluación Normativa
        </p>
      </div>

      <motion.div 
        layout
        className={`flex flex-col xl:flex-row gap-8 w-full items-start justify-center transition-all duration-700 ease-in-out ${enqueuedTasks.length > 0 && !loading ? 'max-w-7xl' : 'max-w-3xl'}`}
      >
        
        {/* COLUMNA IZQUIERDA: ZONA DE SUBIDA */}
        <motion.div 
          layout
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full xl:w-1/3 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-[2rem] p-8 shadow-2xl relative overflow-hidden flex flex-col"
        >
          <div 
            className={`relative border-2 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
              ${isDragging ? "border-indigo-500 bg-indigo-500/10 scale-[1.02]" : "border-slate-700 hover:border-indigo-400 hover:bg-slate-800/50"}
              ${files.length > 0 && !loading && enqueuedTasks.length === 0 ? "border-emerald-500/50 bg-emerald-500/5" : ""}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              accept="application/pdf" 
              multiple
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
            />
            
            <svg className={`w-12 h-12 mb-4 transition-colors duration-300 ${files.length > 0 ? 'text-emerald-400' : 'text-slate-500 group-hover:text-indigo-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            
            {files.length > 0 ? (
              <div className="text-center w-full">
                <p className="text-md font-medium text-emerald-300 mb-2">{files.length} archivo(s) listo(s)</p>
                <div className="max-h-24 overflow-y-auto text-xs text-slate-400 space-y-1 scrollbar-thin scrollbar-thumb-slate-700">
                  {files.map((f, i) => <p key={i} className="truncate">{f.name}</p>)}
                </div>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-slate-300 text-sm mb-1">Arrastra PDFs aquí</p>
                <p className="text-indigo-400 font-semibold text-xs">Explorar lote</p>
              </div>
            )}
          </div>

          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs text-center"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-6 flex justify-center">
            <button 
              onClick={procesarDocumentos}
              disabled={files.length === 0 || loading}
              className={`w-full relative overflow-hidden py-3 rounded-xl font-bold text-sm tracking-wide transition-all duration-300
                ${files.length === 0 || loading 
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed" 
                  : "bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)]"
                }
              `}
            >
              {loading ? "Encolando..." : "Enviar a Celery"}
            </button>
          </div>
        </motion.div>

        {/* COLUMNA DERECHA: RESULTADOS Y COLA */}
        <AnimatePresence mode="wait">
          {enqueuedTasks.length > 0 && !loading && (
            <motion.div 
              layout
              initial={{ opacity: 0, x: 50, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 50, scale: 0.95 }}
              transition={{ duration: 0.6, type: "spring", bounce: 0.4 }}
              className="w-full xl:w-2/3 flex flex-col gap-4"
            >
              {enqueuedTasks.map((task, idx) => {
                const completado = task.status === "COMPLETADO";
                const errorApi = task.status === "ERROR";
                const pendiente = task.status === "EN COLA" || task.status === "PROCESANDO";
                const theme = completado && task.resultado ? getThemeVars(task.resultado.veredicto) : null;

                return (
                  <motion.div 
                    layout
                    key={task.task_id}
                    className={`w-full p-6 rounded-[1.5rem] bg-slate-900/80 backdrop-blur-xl border shadow-xl relative overflow-hidden transition-all duration-500
                      ${completado && theme ? theme.border : pendiente ? "border-indigo-500/50" : "border-rose-500/50"}
                    `}
                  >
                    {/* Background glow para tareas completadas */}
                    {completado && theme && (
                      <div className={`absolute top-0 left-0 w-full h-full ${theme.bgInfo} opacity-20 pointer-events-none`} />
                    )}

                    <div className="relative z-10 flex flex-col md:flex-row gap-6 items-start md:items-center">
                      
                      {/* Estado y Título */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          {pendiente && (
                            <span className="flex items-center gap-2 text-xs font-bold px-2.5 py-1 bg-indigo-500/20 text-indigo-400 rounded-full border border-indigo-500/30">
                              <svg className="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                              EN COLA
                            </span>
                          )}
                          {completado && task.resultado && (
                            <span className={`text-xs font-black px-2.5 py-1 rounded-full border ${theme?.textInfo} bg-slate-900 shadow-sm border-current`}>
                              {task.resultado.veredicto}
                            </span>
                          )}
                          {errorApi && (
                            <span className="text-xs font-bold px-2.5 py-1 bg-rose-500/20 text-rose-400 rounded-full border border-rose-500/30">
                              ERROR
                            </span>
                          )}
                        </div>
                        <h3 className="text-lg font-bold text-slate-200 truncate" title={task.documento}>{task.documento}</h3>
                        
                        {completado && task.resultado && (
                          <div className="mt-2 text-sm text-slate-400 line-clamp-2">
                            <span className="font-semibold text-slate-300">Indicador asignado:</span> {task.resultado.indicador_evaluado}
                          </div>
                        )}
                      </div>

                      {/* Porcentaje Visual (solo si está completado) */}
                      {completado && task.resultado && theme && (
                        <div className="shrink-0 flex items-center gap-4">
                          <div className={`w-16 h-16 rounded-full border-4 flex items-center justify-center ${theme.border} ${theme.bgInfo}`}>
                            <span className={`text-xl font-black ${theme.textInfo}`}>{task.resultado.porcentaje_estimado}%</span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Reporte Expandible */}
                    {completado && task.resultado && (
                      <motion.div 
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="mt-6 pt-4 border-t border-slate-700/50"
                      >
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Justificación del Auditor</h4>
                        <p className="text-sm text-slate-300 bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                          {task.resultado.justificacion}
                        </p>
                      </motion.div>
                    )}

                    {errorApi && (
                      <div className="mt-4 p-3 bg-rose-950/50 rounded-lg border border-rose-800 text-sm text-rose-300">
                        {task.error || "Ocurrió un error inesperado al procesar el archivo en Celery."}
                      </div>
                    )}

                  </motion.div>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>

      </motion.div>
    </div>
  );
}
