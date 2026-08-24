"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";

/**
 * Valida un número de teléfono ecuatoriano:
 *  - Formato local:  09XXXXXXXX  (10 dígitos, empieza con 0)
 *  - Formato internacional: +593 9XXXXXXXX  ó +5939XXXXXXXX
 *
 * Acepta espacios opcionales después del código de país.
 */
function isValidPhone(raw: string): boolean {
  const cleaned = raw.replace(/\s+/g, "");

  // Formato local: exactamente 10 dígitos empezando en 0
  if (/^0\d{9}$/.test(cleaned)) return true;

  // Formato internacional: +593 seguido de 9 dígitos (sin el 0 inicial)
  if (/^\+593\d{9}$/.test(cleaned)) return true;

  return false;
}

export default function LoginPage() {
  const { user, login } = useAuth();
  const router = useRouter();

  // Si ya tiene sesión, ir directo al dashboard
  useEffect(() => {
    if (user) router.replace("/");
  }, [user, router]);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string; phone?: string }>({});
  const [showPassword, setShowPassword] = useState(false);

  const validate = (): boolean => {
    const next: typeof errors = {};

    // Email
    if (!email.trim()) {
      next.email = "El correo es obligatorio.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      next.email = "Ingresa un correo válido.";
    }

    // Password
    if (!password) {
      next.password = "La contraseña es obligatoria.";
    } else if (password.length < 6) {
      next.password = "Mínimo 6 caracteres.";
    }

    // Phone
    if (!phone.trim()) {
      next.phone = "El teléfono es obligatorio.";
    } else if (!isValidPhone(phone.trim())) {
      next.phone = "Formato inválido. Ej: 0987654321 o +593 987654321";
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    // Solo guardar en frontend — no hay backend de auth
    login({ email: email.trim(), phone: phone.trim() });
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-[#020617] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] flex items-center justify-center p-6 font-sans text-slate-200">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-[2rem] p-10 shadow-2xl"
      >
        {/* Encabezado */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 tracking-tight">
            Auditor IA
          </h1>
          <p className="text-slate-400 text-sm mt-2">Inicia sesión para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Correo electrónico
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="usuario@ejemplo.com"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: undefined })); }}
              className={`w-full px-4 py-3 rounded-xl bg-slate-950/60 border text-sm text-slate-200 placeholder-slate-600 outline-none transition-all focus:ring-2
                ${errors.email ? "border-rose-500/60 focus:ring-rose-500/30" : "border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/30"}`}
            />
            {errors.email && <p className="mt-1.5 text-xs text-rose-400">{errors.email}</p>}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Contraseña
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: undefined })); }}
                className={`w-full px-4 py-3 pr-12 rounded-xl bg-slate-950/60 border text-sm text-slate-200 placeholder-slate-600 outline-none transition-all focus:ring-2
                  ${errors.password ? "border-rose-500/60 focus:ring-rose-500/30" : "border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/30"}`}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-indigo-400 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                )}
              </button>
            </div>
            {errors.password && <p className="mt-1.5 text-xs text-rose-400">{errors.password}</p>}
          </div>

          {/* Phone */}
          <div>
            <label htmlFor="phone" className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Teléfono
            </label>
            <input
              id="phone"
              type="tel"
              autoComplete="tel"
              placeholder="0987654321 ó +593 987654321"
              value={phone}
              onChange={(e) => { setPhone(e.target.value); setErrors((p) => ({ ...p, phone: undefined })); }}
              className={`w-full px-4 py-3 rounded-xl bg-slate-950/60 border text-sm text-slate-200 placeholder-slate-600 outline-none transition-all focus:ring-2
                ${errors.phone ? "border-rose-500/60 focus:ring-rose-500/30" : "border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/30"}`}
            />
            {errors.phone && <p className="mt-1.5 text-xs text-rose-400">{errors.phone}</p>}
            <p className="mt-1.5 text-[11px] text-slate-600">10 dígitos locales o con código +593</p>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-3.5 mt-2 rounded-xl font-bold text-base tracking-wide bg-indigo-600 hover:bg-indigo-500 active:scale-[0.98] text-white shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] transition-all duration-300"
          >
            Iniciar sesión
          </button>
        </form>
      </motion.div>
    </div>
  );
}
