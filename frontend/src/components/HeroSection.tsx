import { Sparkles, Sword, Shield } from "lucide-react";

const HeroSection = () => {
  return (
    <section className="relative py-16 px-4 text-center overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 gradient-hero" />
      <div className="absolute top-10 left-10 text-gold/20 animate-float">
        <Sword className="w-12 h-12" />
      </div>
      <div className="absolute top-20 right-16 text-gold/20 animate-float" style={{ animationDelay: '1s' }}>
        <Shield className="w-10 h-10" />
      </div>
      <div className="absolute bottom-20 left-1/4 text-gold/20 animate-float" style={{ animationDelay: '2s' }}>
        <Sparkles className="w-8 h-8" />
      </div>

      <div className="relative z-10 max-w-2xl mx-auto space-y-6">
        {/* Decorative line */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className="h-px w-16 bg-gradient-to-r from-transparent to-gold/50" />
          <Sparkles className="w-5 h-5 text-gold animate-glow" />
          <div className="h-px w-16 bg-gradient-to-l from-transparent to-gold/50" />
        </div>

        <h1 className="text-4xl md:text-5xl lg:text-6xl font-medieval text-gold tracking-wider leading-tight">
          전생체험카드
        </h1>
        
        <p className="text-xl md:text-2xl text-parchment/80 font-body italic">
          당신의 중세 시대 전생을 발견하세요
        </p>

        <div className="pt-4 space-y-3">
          <p className="text-muted-foreground font-body leading-relaxed max-w-lg mx-auto">
            사진 한 장으로 당신의 숨겨진 RPG 스탯과 
            <br className="hidden sm:block" />
            중세 판타지 캐릭터를 만나보세요
          </p>
        </div>

        {/* Decorative line */}
        <div className="flex items-center justify-center gap-4 pt-6">
          <div className="h-px w-24 bg-gradient-to-r from-transparent via-gold/30 to-transparent" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
