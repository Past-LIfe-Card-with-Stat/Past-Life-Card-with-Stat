import { cn } from "@/lib/utils";

interface StatBarProps {
  label: string;
  value: number;
  maxValue?: number;
  colorClass: string;
  icon: React.ReactNode;
}

const StatBar = ({ label, value, maxValue = 100, colorClass, icon }: StatBarProps) => {
  const percentage = Math.min((value / maxValue) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gold">{icon}</span>
          <span className="font-medieval text-parchment tracking-wide">{label}</span>
        </div>
        <span className="font-medieval text-gold">{value}</span>
      </div>
      <div className="h-3 bg-secondary rounded-full overflow-hidden border border-gold/20">
        <div
          className={cn("h-full rounded-full transition-all duration-1000 ease-out", colorClass)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default StatBar;
