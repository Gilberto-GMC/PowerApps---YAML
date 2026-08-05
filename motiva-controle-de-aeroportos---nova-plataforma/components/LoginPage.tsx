
import React, { useState } from 'react';
import { User, Lock, Eye, EyeOff, ArrowRight, Loader2, Plane } from 'lucide-react';
import logoMotiva from '../src/assets/images/regenerated_image_1778428990774.png';

const MotivaLogo = ({ className }: { className?: string }) => (
  <img 
    src={logoMotiva}
    alt="Motiva Logo"
    className={`object-contain ${className}`}
  />
);

// Added interface for LoginPageProps to fix missing name error on line 17
interface LoginPageProps {
  onLogin: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    setTimeout(() => {
      if (username === 'admin' && password === 'admin') {
        onLogin();
      } else {
        setError('Credenciais inválidas. Tente novamente.');
        setIsLoading(false);
      }
    }, 1000);
  };

  return (
    <div className="min-h-screen w-full flex bg-slate-50 font-sans">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-[#391694] flex-col justify-between">
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2074&auto=format&fit=crop" 
            alt="Motiva Background" 
            className="w-full h-full object-cover opacity-90"
          />
          <div className="absolute inset-0 bg-[#391694]/40 mix-blend-multiply"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-[#391694]/90 via-transparent to-transparent"></div>
        </div>

        <div className="relative z-10 h-full flex flex-col justify-between p-12 text-white">
          <div className="flex items-center gap-3"></div>
          <div className="flex flex-col items-center justify-center">
             <div className="bg-white/20 w-40 h-40 flex items-center justify-center rounded-none backdrop-blur-md mb-8 shadow-2xl border border-white/20 hover:scale-105 transition-transform duration-500">
              <MotivaLogo className="w-[115px] h-[115px] text-white" />
            </div>
            <h1 className="text-6xl font-bold tracking-tighter mb-2">AeroMotiva</h1>
            <p className="text-xl text-indigo-100 tracking-wide font-light">Controle Aeroportuário</p>
          </div>

          <div className="flex justify-between items-center text-xs text-indigo-100/80 pt-6 border-t border-white/10">
            <p>© 2025 Motiva Aeroportos. Todos os direitos reservados.</p>
            <div className="flex gap-4">
              <span className="hover:text-white cursor-pointer transition-colors">Privacidade</span>
              <span className="hover:text-white cursor-pointer transition-colors">Termos</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-12 lg:p-24 bg-white relative">
        <div className="lg:hidden absolute top-8 left-8 flex items-center gap-3">
            <div className="bg-[#391694] p-2.5 rounded-none shadow-lg">
              <MotivaLogo className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-slate-800 text-xl tracking-tight">AeroMotiva</span>
        </div>

        <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Bem-vindo</h2>
            <p className="mt-2 text-slate-500">
              Entre com suas credenciais para acessar o painel.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium text-slate-700 block">
                Usuário
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-slate-400 group-focus-within:text-[#391694] transition-colors" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-none bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-[#391694]/20 focus:border-[#391694] transition-all duration-200"
                  placeholder="Digite seu usuário"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium text-slate-700 block">
                  Senha
                </label>
                <a href="#" className="text-sm font-medium text-[#391694] hover:text-[#2a106e] transition-colors">
                  Esqueceu a senha?
                </a>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-[#391694] transition-colors" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-10 py-3 border border-slate-200 rounded-none bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-[#391694]/20 focus:border-[#391694] transition-all duration-200"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-none bg-red-50 border border-red-100 text-sm text-red-600 flex items-center gap-2 animate-in slide-in-from-top-2">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
                {error}
              </div>
            )}

            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-[#391694] focus:ring-[#391694] border-slate-300 rounded-none cursor-pointer"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-600 cursor-pointer select-none">
                Manter conectado por 30 dias
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center py-3.5 px-4 border border-transparent rounded-none shadow-md text-sm font-bold text-white bg-[#391694] hover:bg-[#2a106e] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#391694] disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Autenticando...
                </>
              ) : (
                <>
                  Entrar
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-400">
             Versão 1.0.0
          </div>
        </div>
      </div>
    </div>
  );
};
