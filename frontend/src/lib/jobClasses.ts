import { Sword, Shield, Wand2, Heart, Flame, Skull, Crown, Crosshair } from "lucide-react";

export interface JobClass {
  id: string;
  name: string;
  nameKr: string;
  icon: typeof Sword;
  gradient: string;
  accentColor: string;
  description: string;
}

export const jobClasses: JobClass[] = [
  {
    id: "barbarian",
    name: "Barbarian Warrior",
    nameKr: "바바리안 전사",
    icon: Sword,
    gradient: "from-red-900 via-red-800 to-orange-900",
    accentColor: "text-red-400",
    description: "압도적인 힘과 체력으로 전장을 지배하는 전사",
  },
  {
    id: "knight",
    name: "Holy Knight",
    nameKr: "성기사",
    icon: Shield,
    gradient: "from-blue-900 via-slate-800 to-blue-950",
    accentColor: "text-blue-400",
    description: "정의와 명예를 수호하는 빛의 기사",
  },
  {
    id: "mage",
    name: "Arcane Mage",
    nameKr: "대마법사",
    icon: Wand2,
    gradient: "from-purple-900 via-violet-800 to-indigo-900",
    accentColor: "text-purple-400",
    description: "고대의 마법을 다루는 신비로운 마법사",
  },
  {
    id: "healer",
    name: "Divine Healer",
    nameKr: "신성 치유사",
    icon: Heart,
    gradient: "from-emerald-900 via-teal-800 to-cyan-900",
    accentColor: "text-emerald-400",
    description: "생명의 은총으로 동료를 치유하는 성직자",
  },
  {
    id: "rogue",
    name: "Shadow Rogue",
    nameKr: "암흑 도적",
    icon: Crosshair,
    gradient: "from-gray-900 via-zinc-800 to-neutral-900",
    accentColor: "text-gray-400",
    description: "그림자 속에서 움직이는 치명적인 암살자",
  },
  {
    id: "pyromancer",
    name: "Pyromancer",
    nameKr: "화염술사",
    icon: Flame,
    gradient: "from-orange-900 via-amber-800 to-yellow-900",
    accentColor: "text-orange-400",
    description: "불꽃의 힘을 다루는 파괴의 마법사",
  },
  {
    id: "necromancer",
    name: "Necromancer",
    nameKr: "강령술사",
    icon: Skull,
    gradient: "from-slate-900 via-gray-900 to-zinc-950",
    accentColor: "text-slate-400",
    description: "죽음의 힘을 다루는 어둠의 마법사",
  },
  {
    id: "monarch",
    name: "Noble Monarch",
    nameKr: "귀족 군주",
    icon: Crown,
    gradient: "from-amber-900 via-yellow-800 to-gold",
    accentColor: "text-amber-400",
    description: "타고난 카리스마로 왕국을 다스리는 군주",
  },
];

export const getJobClass = (id: string): JobClass => {
  return jobClasses.find((job) => job.id === id) || jobClasses[0];
};

export const getRandomJobClass = (): JobClass => {
  return jobClasses[Math.floor(Math.random() * jobClasses.length)];
};
