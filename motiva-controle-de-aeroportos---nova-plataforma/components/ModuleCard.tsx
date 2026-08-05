
import React from 'react';
import { ModuleItem } from '../types';
import { ArrowRight, Star } from 'lucide-react';

interface ModuleCardProps {
  module: ModuleItem;
  onClick: (module: ModuleItem) => void;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ module, onClick }) => {
  const Icon = module.icon;

  const getIconStyles = () => {
    switch (module.category) {
      case 'inspections':
        return 'bg-[#FFF5F0] text-[#D95D39]';
      case 'operational':
        return 'bg-[#F0FDFF] text-[#0891b2]';
      case 'fauna':
        return 'bg-[#EEFFE6] text-[#166534]';
      case 'safety_events':
        return 'bg-[#FDF4FF] text-[#c026d3]';
      case 'aeronautical_info':
        return 'bg-[#F5F3FF] text-[#391694]';
      case 'orientation_program':
        return 'bg-[#FFFD8A] text-[#858316]';
      default:
        return 'bg-slate-50 text-slate-600';
    }
  };

  return (
    <div 
      onClick={() => onClick(module)}
      className="group relative bg-white rounded-none p-8 border border-[#C9C5E6] transition-all duration-300 hover:bg-[#F5F3FF] hover:shadow-xl cursor-pointer h-full flex flex-col justify-between"
    >
      <div className="flex flex-col items-center text-center gap-6">
        <div className={`p-5 rounded-none transition-all duration-300 shadow-sm ${getIconStyles()}`}>
          <Icon className="w-10 h-10" strokeWidth={1} />
        </div>
        
        <div className="space-y-3">
          <h3 className="font-bold text-slate-800 text-xl leading-tight tracking-normal transition-colors duration-300 group-hover:text-[#391694]">
            {module.title}
          </h3>
          <p className="text-sm text-slate-400 group-hover:text-slate-500 line-clamp-2 min-h-[3em] leading-relaxed font-normal">
             {module.description}
          </p>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-slate-50 flex items-center justify-between text-[#391694] font-bold text-xs uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
        <span>Acessar Módulo</span>
        <ArrowRight className="w-5 h-5" strokeWidth={1} />
      </div>
      
      <div className="absolute top-6 right-6 opacity-30 group-hover:opacity-100 transition-all">
        <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-[#391694]" strokeWidth={1} />
      </div>
    </div>
  );
};
