import { useState } from "react";
import { ArrowRight, RotateCcw, History, Plus } from "lucide-react";
import HeroSection from "@/components/HeroSection";
import ImageUploader from "@/components/ImageUploader";
import CharacterCard from "@/components/CharacterCard";
import CharacterGallery from "@/components/CharacterGallery";
import ValidationErrorDialog, {
  ValidationError,
  ValidationErrorType,
} from "@/components/ValidationErrorDialog";
import { Button } from "@/components/ui/button";
import {
  useCharacterHistory,
  CharacterData,
} from "@/hooks/useCharacterHistory";
import { jobClasses } from "@/lib/jobClasses";

// 검증 에러 메시지
const validationMessages: Record<ValidationErrorType, string> = {
  no_human: "사람이 감지되지 않았습니다. 몬스터는 아직 지원하지 않아요!",
  no_person: "이미지에서 사람을 감지할 수 없습니다. 전신 사진을 사용해주세요.",
  not_fullbody: "전신 사진이 필요해요. 발끝까지 나와야 스탯을 잴 수 있습니다!",
  animal_detected: "앗, 귀여운 동물이군요! 하지만 지금은 사람만 변환 가능합니다.",
  image_too_small: "이미지가 너무 작습니다. 최소 256x256 픽셀 이상의 이미지를 사용해주세요.",
  image_too_large: "이미지가 너무 큽니다. 최대 4096x4096 픽셀 이하의 이미지를 사용해주세요.",
  image_corrupted: "이미지 파일이 손상되었거나 지원하지 않는 형식입니다.",
  no_face_warning: "얼굴을 명확하게 감지할 수 없습니다. Face Swap 기능이 제한될 수 있습니다.",
  unsupported_format: "JPG, PNG 형식의 이미지 파일만 지원합니다.",
};

// Backend API 응답 타입
interface ApiStatBar {
  value: number;
  max: number;
}

interface ApiStats {
  STR: ApiStatBar;
  AGI: ApiStatBar;
  INT: ApiStatBar;
  CHA: ApiStatBar;
  LUK: ApiStatBar;
  VIT: ApiStatBar;
}

interface ApiCardData {
  identity: {
    job_title: string;
    role: string;
  };
  stats: ApiStats | null;
  flavor_text: string;
}

interface ApiMetadata {
  original_filename: string;
  image_size: string;
  output_size: string;
}

interface ApiResponse {
  status: string;
  card_data: ApiCardData;
  medieval_image: string;
  output_path: string;
  metadata: ApiMetadata;
}

// Backend job_title을 Frontend jobClass로 매핑
const mapJobTitle = (jobTitle: string): { id: string; nameKr: string } => {
  const jobMapping: Record<string, string> = {
    전사: "barbarian",
    방패병: "knight",
    기사: "knight",
    암살자: "rogue",
    궁수: "rogue",
    지휘관: "monarch",
    기사단장: "monarch",
  };

  const mappedId = jobMapping[jobTitle] || "barbarian";
  const jobClass = jobClasses.find((j) => j.id === mappedId) || jobClasses[0];

  return { id: jobClass.id, nameKr: jobTitle };
};

// 기본 스탯 (stats가 null인 경우 사용)
const defaultStats: ApiStats = {
  STR: { value: 25, max: 50 },
  AGI: { value: 25, max: 50 },
  INT: { value: 25, max: 50 },
  CHA: { value: 25, max: 50 },
  LUK: { value: 25, max: 50 },
  VIT: { value: 25, max: 50 },
};

// API 응답을 Frontend CharacterData 형식으로 변환
const transformApiResponse = (
  apiResponse: ApiResponse,
): Omit<CharacterData, "id" | "createdAt"> => {
  const { card_data, medieval_image } = apiResponse;
  const { identity, stats: rawStats, flavor_text } = card_data;

  // stats가 null이면 기본값 사용
  const stats = rawStats ?? defaultStats;

  const jobInfo = mapJobTitle(identity.job_title);

  // 스탯 총합으로 레벨 계산 (1-50)
  const totalStats =
    stats.STR.value +
    stats.AGI.value +
    stats.INT.value +
    stats.CHA.value +
    stats.LUK.value +
    stats.VIT.value;
  const level = Math.min(50, Math.max(1, Math.floor(totalStats / 6)));

  return {
    name: identity.role,
    jobClassId: jobInfo.id,
    jobClass: jobInfo.nameKr,
    level,
    imageUrl: `data:image/png;base64,${medieval_image}`,
    stats: {
      strength: stats.STR.value * 2, // 50점 만점 → 100점 만점으로 변환
      agility: stats.AGI.value * 2,
      intelligence: stats.INT.value * 2,
      charisma: stats.CHA.value * 2,
      luck: stats.LUK.value * 2,
      vitality: stats.VIT.value * 2,
    },
    description: flavor_text,
  };
};

// 실제 API 호출 함수
const uploadImage = async (file: File): Promise<ApiResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  // Vite 프록시 사용: /api/images/transform → localhost:8000/images/transform
  const response = await fetch("/api/images/transform", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: "알 수 없는 오류" }));
    const message = error.message || "알 수 없는 오류";
    throw new Error(`HTTP_${response.status}:${message}`);
  }

  return response.json();
};

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentCharacter, setCurrentCharacter] =
    useState<CharacterData | null>(null);
  const [showGallery, setShowGallery] = useState(false);
  const [validationError, setValidationError] =
    useState<ValidationError | null>(null);

  const { history, addCharacter, removeCharacter, clearHistory } =
    useCharacterHistory();

  const handleImageSelect = (file: File) => {
    setSelectedFile(file);
    setCurrentCharacter(null);
  };

  const handleGenerate = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setValidationError(null);

    try {
      // FastAPI POST /images/transform 호출
      const apiResponse = await uploadImage(selectedFile);

      if (apiResponse.status !== "success") {
        throw new Error("캐릭터 생성에 실패했습니다.");
      }

      // API 응답을 Frontend 형식으로 변환
      const characterData = transformApiResponse(apiResponse);
      const savedCharacter = addCharacter(characterData);
      setCurrentCharacter(savedCharacter);
    } catch (error) {
      console.error("API 호출 실패:", error);

      // 에러 메시지에 따라 적절한 검증 에러 표시
      const errorMessage =
        error instanceof Error ? error.message : "알 수 없는 오류";

      // 백엔드 검증 에러 파싱
      let errorType: ValidationErrorType = "no_human";
      let customMessage = errorMessage;
      const warnings: string[] = [];

      // HTTP 415: Unsupported Media Type
      if (errorMessage.includes("HTTP_415") || errorMessage.includes("Unsupported Media Type")) {
        errorType = "unsupported_format";
        customMessage = validationMessages.unsupported_format;
      } else if (errorMessage.includes("형식") || errorMessage.includes("format") || errorMessage.includes("extension") || errorMessage.includes("확장자")) {
        errorType = "unsupported_format";
        customMessage = validationMessages.unsupported_format;
      } else if (errorMessage.includes("이미지가 너무 작습니다") || errorMessage.includes("too small")) {
        errorType = "image_too_small";
        customMessage = validationMessages.image_too_small;
      } else if (errorMessage.includes("이미지가 너무 큽니다") || errorMessage.includes("too large")) {
        errorType = "image_too_large";
        customMessage = validationMessages.image_too_large;
      } else if (errorMessage.includes("손상") || errorMessage.includes("corrupted")) {
        errorType = "image_corrupted";
        customMessage = validationMessages.image_corrupted;
      } else if (errorMessage.includes("사람을 감지할 수 없습니다") || errorMessage.includes("no person")) {
        errorType = "no_person";
        customMessage = validationMessages.no_person;
      } else if (errorMessage.includes("얼굴") || errorMessage.includes("face")) {
        errorType = "no_face_warning";
        customMessage = validationMessages.no_face_warning;
      } else if (errorMessage.includes("pose") || errorMessage.includes("person")) {
        errorType = "no_human";
        customMessage = validationMessages.no_human;
      } else if (errorMessage.includes("fullbody") || errorMessage.includes("body")) {
        errorType = "not_fullbody";
        customMessage = validationMessages.not_fullbody;
      } else {
        customMessage = `오류가 발생했습니다: ${errorMessage}`;
      }

      setValidationError({
        type: errorType,
        message: customMessage,
        warnings: warnings.length > 0 ? warnings : undefined,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setCurrentCharacter(null);
    setValidationError(null);
  };

  const handleCloseError = () => {
    setValidationError(null);
  };

  const handleSelectFromGallery = (character: CharacterData) => {
    setCurrentCharacter(character);
    setShowGallery(false);
  };

  return (
    <div className="min-h-screen gradient-hero">
      <HeroSection />

      <main className="container max-w-4xl mx-auto px-4 pb-20">
        {/* Gallery Toggle Button */}
        <div className="flex justify-end mb-6">
          <Button
            variant="dark"
            size="sm"
            onClick={() => {
              setShowGallery(!showGallery);
              if (showGallery) {
                setCurrentCharacter(null);
                setSelectedFile(null);
              }
            }}
            className="gap-2"
          >
            {showGallery ? (
              <>
                <Plus className="w-4 h-4" />
                새로 만들기
              </>
            ) : (
              <>
                <History className="w-4 h-4" />
                히스토리 ({history.length})
              </>
            )}
          </Button>
        </div>

        {showGallery ? (
          <CharacterGallery
            characters={history}
            onSelect={handleSelectFromGallery}
            onDelete={removeCharacter}
            onClearAll={clearHistory}
          />
        ) : !currentCharacter ? (
          <div className="space-y-8">
            <ImageUploader
              onImageSelect={handleImageSelect}
              isLoading={isLoading}
            />

            {selectedFile && !isLoading && (
              <div className="flex justify-center">
                <Button
                  variant="gold"
                  size="xl"
                  onClick={handleGenerate}
                  className="group"
                >
                  전생 캐릭터 생성
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-8 animate-in fade-in duration-700">
            <CharacterCard {...currentCharacter} />

            <div className="flex justify-center gap-4">
              <Button variant="dark" size="lg" onClick={handleReset}>
                <RotateCcw className="w-4 h-4 mr-2" />
                다시 하기
              </Button>
              <Button variant="gold" size="lg">
                카드 저장하기
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-8 text-center border-t border-gold/10">
        <p className="text-muted-foreground text-sm font-body">
          ⚔️ 전생체험카드 - 당신의 중세 캐릭터를 발견하세요 ⚔️
        </p>
      </footer>

      {/* Validation Error Dialog */}
      <ValidationErrorDialog
        error={validationError}
        onClose={handleCloseError}
      />
    </div>
  );
};

export default Index;
