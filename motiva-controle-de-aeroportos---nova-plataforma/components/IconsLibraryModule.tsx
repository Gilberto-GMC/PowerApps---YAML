
import React, { useState } from 'react';
import { 
  Download, 
  Search, 
  Palette, 
  Check,
  // System Icons
  Globe, FileText, AlertTriangle, LayoutGrid, PlaneLanding, ScanLine, ShieldCheck, 
  Building, CloudLightning, Fan, Truck, Flag, Megaphone, ArrowRightLeft, Droplets, 
  Trash2, Wind, AlertOctagon, Car, UserX, HardHat, FileQuestion, Accessibility,
  Home, Plane, Settings, LogOut, Siren, Lock, BookOpen, Lightbulb, Shield, Building2,
  Sparkles, ArrowLeft, List, ChevronRight, ArrowRight, BarChart3, Activity, AlertCircle, 
  PlaneTakeoff, Clock, Bell, User, Filter, CheckCircle2, X, PlusCircle, History, Calendar,
  MoreHorizontal, Pencil, ExternalLink, Map, Radio, Fuel, CloudSun, RotateCcw, Navigation, 
  Info, MapIcon, ClipboardCheck, Eye, EyeOff, Loader2, Send, XCircle, ChevronDown, CornerUpLeft
} from 'lucide-react';

// Map of all icons used in the system
const SYSTEM_ICONS = {
  // Navigation & UI
  Home, Settings, Search, Bell, User, LogOut, Menu: List, Filter, 
  ArrowLeft, ArrowRight, ChevronRight, ChevronDown, PlusCircle, History,
  X, Check, CheckCircle2, AlertCircle, AlertTriangle, Info, Loader2,
  Eye, EyeOff, MoreHorizontal, Pencil, Trash2, Download, Palette,
  ExternalLink, Calendar, Clock,
  
  // Modules - Operational
  Plane, PlaneLanding, PlaneTakeoff, Truck, Car, Fan, Wind, CloudLightning,
  CloudSun, Flag, ArrowRightLeft, Accessibility, Fuel, Map, Navigation,
  
  // Modules - Safety & Security
  Shield, ShieldCheck, Lock, Siren, AlertOctagon, Droplets, Fire: Siren, 
  HardHat, UserX, ScanLine,
  
  // Modules - Admin & AIS
  Building, Building2, Globe, FileText, FileQuestion, BookOpen, Lightbulb,
  Sparkles, BarChart3, Activity, LayoutGrid, MapIcon, Radio, RotateCcw,
  ClipboardCheck, Send, XCircle, CornerUpLeft
};

const BRAND_COLORS = [
  { label: 'Brand', value: '#391694' },
  { label: 'Cyan', value: '#0891b2' },
  { label: 'Orange', value: '#D95D39' },
  { label: 'Fuchsia', value: '#c026d3' },
  { label: 'Slate', value: '#475569' },
  { label: 'Black', value: '#000000' },
];

export const IconsLibraryModule: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedColor, setSelectedColor] = useState('#391694');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const filteredIcons = Object.entries(SYSTEM_ICONS).filter(([name]) => 
    name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDownload = (name: string, IconComponent: any) => {
    setDownloadingId(name);
    
    // Create a temporary SVG element to serialize
    // We construct the SVG string manually to ensure clean output
    // Lucide icons are 24x24 by default
    const svgString = `
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${selectedColor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        ${document.getElementById(`icon-svg-${name}`)?.innerHTML || ''}
      </svg>
    `;

    const blob = new Blob([svgString.trim()], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${name}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => setDownloadingId(null), 500);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      {/* Header Area */}
      <div className="bg-white border-b border-slate-200 px-8 py-6 flex flex-col gap-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-3">
            <Palette className="w-6 h-6 text-[#391694]" />
            Biblioteca de Ícones
          </h2>
          <p className="text-slate-500 mt-1">
            Visualize e faça o download dos ícones utilizados no Design System da Motiva.
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-6 items-end md:items-center justify-between">
          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-6 w-full md:w-auto">
            {/* Search */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Buscar ícone..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-none text-sm outline-none focus:border-[#391694] transition-all"
              />
            </div>

            {/* Color Picker */}
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5 p-1 bg-slate-100 rounded-none border border-slate-200">
                {BRAND_COLORS.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setSelectedColor(color.value)}
                    className="w-6 h-6 rounded-none border border-black/10 transition-transform hover:scale-110 relative"
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  >
                    {selectedColor === color.value && (
                      <Check className="w-3 h-3 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 drop-shadow-md" strokeWidth={3} />
                    )}
                  </button>
                ))}
              </div>
              <div className="relative group">
                <input 
                  type="color" 
                  value={selectedColor}
                  onChange={(e) => setSelectedColor(e.target.value)}
                  className="w-8 h-8 p-0 border-0 rounded-none cursor-pointer opacity-0 absolute inset-0"
                />
                <div 
                  className="w-8 h-8 rounded-none border border-slate-300 flex items-center justify-center bg-white group-hover:border-slate-400 cursor-pointer"
                  style={{ background: `linear-gradient(135deg, ${selectedColor} 50%, #fff 50%)` }}
                >
                  <Palette className="w-4 h-4 text-slate-500 mix-blend-difference" />
                </div>
              </div>
              <span className="text-xs font-mono text-slate-500 uppercase">{selectedColor}</span>
            </div>
          </div>
          
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            {filteredIcons.length} Ícones Encontrados
          </div>
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
          {filteredIcons.map(([name, Icon]) => (
            <div 
              key={name}
              className="group bg-white border border-slate-200 p-4 flex flex-col items-center justify-between gap-4 hover:border-[#391694] hover:shadow-lg transition-all aspect-square relative"
            >
              <div 
                className="flex-1 flex items-center justify-center w-full relative"
                style={{ color: selectedColor }}
              >
                {/* Render icon with ID for extraction */}
                <Icon 
                  id={`icon-svg-${name}`}
                  className="w-8 h-8 transition-transform group-hover:scale-110" 
                  strokeWidth={1.5} 
                />
                
                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-white/90 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button
                    onClick={() => handleDownload(name, Icon)}
                    className="p-2 bg-[#391694] text-white rounded-none hover:bg-[#2a106e] transition-colors shadow-sm"
                    title="Baixar SVG"
                  >
                    {downloadingId === name ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
              
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider truncate w-full text-center select-all group-hover:text-[#391694]">
                {name}
              </span>
            </div>
          ))}
        </div>
        
        {filteredIcons.length === 0 && (
          <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <Search className="w-12 h-12 mb-4 opacity-20" />
            <p className="font-medium">Nenhum ícone encontrado para "{searchQuery}"</p>
          </div>
        )}
      </div>
    </div>
  );
};
