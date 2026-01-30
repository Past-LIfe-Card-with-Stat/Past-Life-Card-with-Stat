import { Trash2, Eye, Clock, Scroll } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CharacterData } from "@/hooks/useCharacterHistory";
import { getJobClass } from "@/lib/jobClasses";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";

interface CharacterGalleryProps {
  characters: CharacterData[];
  onSelect: (character: CharacterData) => void;
  onDelete: (id: string) => void;
  onClearAll: () => void;
}

const CharacterGallery = ({
  characters,
  onSelect,
  onDelete,
  onClearAll,
}: CharacterGalleryProps) => {
  if (characters.length === 0) {
    return (
      <div className="text-center py-12 px-4">
        <Scroll className="w-16 h-16 mx-auto text-gold/40 mb-4" />
        <h3 className="text-xl font-medieval text-gold/60 mb-2">
          아직 생성된 캐릭터가 없습니다
        </h3>
        <p className="text-muted-foreground font-body">
          사진을 업로드하여 첫 번째 중세 캐릭터를 만들어보세요!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-medieval text-gold flex items-center gap-2">
          <Clock className="w-5 h-5" />
          생성 히스토리
        </h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearAll}
          className="text-destructive hover:text-destructive hover:bg-destructive/10"
        >
          <Trash2 className="w-4 h-4 mr-1" />
          전체 삭제
        </Button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {characters.map((character) => {
          const jobClass = getJobClass(character.jobClassId);
          const JobIcon = jobClass.icon;

          return (
            <div
              key={character.id}
              className={`group relative rounded-lg overflow-hidden border border-gold/20 
                bg-gradient-to-br ${jobClass.gradient} 
                hover:border-gold/50 transition-all duration-300 hover:scale-105 cursor-pointer`}
              onClick={() => onSelect(character)}
            >
              {/* Character Image */}
              <div className="aspect-[3/4] relative">
                <img
                  src={character.imageUrl}
                  alt={character.name}
                  className="w-full h-full object-cover"
                />
                {/* Overlay gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                {/* Job Icon Badge */}
                <div className={`absolute top-2 right-2 p-1.5 rounded-full bg-black/50 ${jobClass.accentColor}`}>
                  <JobIcon className="w-4 h-4" />
                </div>

                {/* Character Info */}
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <div className="flex items-center gap-1 mb-1">
                    <span className="text-xs text-gold/80 font-medieval">
                      Lv.{character.level}
                    </span>
                  </div>
                  <h4 className="text-sm font-medieval text-gold truncate">
                    {character.name}
                  </h4>
                  <p className="text-xs text-parchment/70 font-body truncate">
                    {character.jobClass}
                  </p>
                  <p className="text-xs text-muted-foreground/60 mt-1">
                    {formatDistanceToNow(new Date(character.createdAt), {
                      addSuffix: true,
                      locale: ko,
                    })}
                  </p>
                </div>
              </div>

              {/* Hover Actions */}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <Button
                  variant="gold"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(character);
                  }}
                >
                  <Eye className="w-4 h-4 mr-1" />
                  보기
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-destructive hover:bg-destructive/20"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(character.id);
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CharacterGallery;
