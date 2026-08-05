
import { LucideIcon } from "lucide-react";

export type CategoryId = 'aeronautical_info' | 'inspections' | 'operational' | 'safety_events' | 'fauna' | 'orientation_program';

export interface ModuleItem {
  id: string;
  title: string;
  category: CategoryId;
  icon: LucideIcon;
  description?: string;
  isFavorite?: boolean;
}

export interface CategoryDefinition {
  id: CategoryId;
  label: string;
  description: string;
  colorClass: string; // Used for badges
  themeColor: string; // Used for dynamic borders/text
}

export type ViewState = 'dashboard' | 'module-detail';
