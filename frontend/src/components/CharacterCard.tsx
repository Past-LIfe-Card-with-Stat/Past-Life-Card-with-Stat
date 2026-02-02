import { Sword, Wind, Brain, Heart, Sparkles, Shield } from "lucide-react";
import { forwardRef } from "react";
import StatBar from "./StatBar";
import { getJobClass, JobClass } from "@/lib/jobClasses";

interface CharacterStats {
  strength: number;
  agility: number;
  intelligence: number;
  charisma: number;
  luck: number;
  vitality: number;
}

interface CharacterCardProps {
  name: string;
  jobClassId: string;
  jobClass: string;
  level: number;
  imageUrl: string;
  stats: CharacterStats;
  description: string;
}

const CharacterCard = forwardRef<HTMLDivElement, CharacterCardProps>((
  {
    name,
    jobClassId,
    jobClass,
    level,
    imageUrl,
    stats,
    description,
  },
  ref,
) => {
  const jobClassData = getJobClass(jobClassId);
  const JobIcon = jobClassData.icon;

  return (
    <div className="relative w-full max-w-md mx-auto" ref={ref}>
      {/* Decorative corners */}
      <div className="absolute -top-2 -left-2 w-8 h-8 border-t-2 border-l-2 border-gold" />
      <div className="absolute -top-2 -right-2 w-8 h-8 border-t-2 border-r-2 border-gold" />
      <div className="absolute -bottom-2 -left-2 w-8 h-8 border-b-2 border-l-2 border-gold" />
      <div className="absolute -bottom-2 -right-2 w-8 h-8 border-b-2 border-r-2 border-gold" />

      <div className={`relative rounded-lg overflow-hidden shadow-card p-6 border-2 border-gold/40 bg-gradient-to-br ${jobClassData.gradient}`}>
        {/* Job Class Icon Badge */}
        <div className={`absolute top-4 right-4 p-2 rounded-full bg-black/30 ${jobClassData.accentColor}`}>
          <JobIcon className="w-6 h-6" />
        </div>

        {/* Header */}
        <div className="text-center mb-4">
          <div className={`inline-block px-4 py-1 bg-black/30 rounded-full border border-gold/30 mb-2`}>
            <span className="text-gold font-medieval text-sm">Lv. {level}</span>
          </div>
          <h2 className="text-2xl font-medieval text-gold tracking-wider">{jobClass}</h2>
          <p className={`font-body italic ${jobClassData.accentColor}`}>『 {name} 』</p>
        </div>

        {/* Character Image */}
        <div className="relative mb-6">
          <div className="aspect-[3/4] rounded-lg overflow-hidden border-2 border-gold/30 shadow-gold">
            <img
              src={imageUrl}
              alt={name}
              className="w-full h-full object-cover"
            />
          </div>
          {/* Shimmer effect */}
          <div className="absolute inset-0 rounded-lg animate-shimmer pointer-events-none" />
        </div>

        {/* Stats */}
        <div className="space-y-3 mb-6">
          <StatBar
            label="힘 (STR)"
            value={stats.strength}
            colorClass="stat-strength"
            icon={<Sword className="w-4 h-4" />}
          />
          <StatBar
            label="민첩 (AGI)"
            value={stats.agility}
            colorClass="stat-agility"
            icon={<Wind className="w-4 h-4" />}
          />
          <StatBar
            label="지능 (INT)"
            value={stats.intelligence}
            colorClass="stat-intelligence"
            icon={<Brain className="w-4 h-4" />}
          />
          <StatBar
            label="매력 (CHA)"
            value={stats.charisma}
            colorClass="stat-charisma"
            icon={<Heart className="w-4 h-4" />}
          />
          <StatBar
            label="행운 (LUK)"
            value={stats.luck}
            colorClass="stat-luck"
            icon={<Sparkles className="w-4 h-4" />}
          />
          <StatBar
            label="체력 (VIT)"
            value={stats.vitality}
            colorClass="stat-vitality"
            icon={<Shield className="w-4 h-4" />}
          />
        </div>

        {/* Description */}
        <div className="p-4 bg-secondary/50 rounded-lg border border-gold/20">
          <p className="text-parchment/90 font-body text-center italic leading-relaxed">
            "{description}"
          </p>
        </div>
      </div>
    </div>
  );
});

CharacterCard.displayName = "CharacterCard";

export default CharacterCard;
