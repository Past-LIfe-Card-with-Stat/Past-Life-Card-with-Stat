import { AlertTriangle, UserX, Footprints, Cat, ImageOff, FileWarning, FileX } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

export type ValidationErrorType = 
  | "no_human" 
  | "not_fullbody" 
  | "animal_detected"
  | "image_too_small"
  | "image_too_large"
  | "image_corrupted"
  | "no_person"
  | "no_face_warning"
  | "unsupported_format";

interface ValidationError {
  type: ValidationErrorType;
  message: string;
  warnings?: string[];
}

const errorConfig: Record<ValidationErrorType, { icon: React.ComponentType<{ className?: string }>; title: string; isWarning?: boolean }> = {
  no_human: {
    icon: UserX,
    title: "사람이 감지되지 않았어요",
  },
  no_person: {
    icon: UserX,
    title: "사람이 감지되지 않았어요",
  },
  not_fullbody: {
    icon: Footprints,
    title: "전신 사진이 필요해요",
  },
  animal_detected: {
    icon: Cat,
    title: "귀여운 동물이군요!",
  },
  image_too_small: {
    icon: ImageOff,
    title: "이미지가 너무 작아요",
  },
  image_too_large: {
    icon: ImageOff,
    title: "이미지가 너무 커요",
  },
  image_corrupted: {
    icon: FileWarning,
    title: "이미지 파일에 문제가 있어요",
  },
  no_face_warning: {
    icon: AlertTriangle,
    title: "얼굴 감지 경고",
    isWarning: true,
  },
  unsupported_format: {
    icon: FileX,
    title: "지원하지 않는 파일 형식이에요",
  },
};

interface ValidationErrorDialogProps {
  error: ValidationError | null;
  onClose: () => void;
}

const ValidationErrorDialog = ({ error, onClose }: ValidationErrorDialogProps) => {
  if (!error) return null;

  const config = errorConfig[error.type];
  const Icon = config.icon;
  const isWarning = config.isWarning || false;

  return (
    <Dialog open={!!error} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md gradient-card border-gold/30">
        <DialogHeader className="text-center">
          <div className={`mx-auto mb-4 w-16 h-16 rounded-full flex items-center justify-center border ${
            isWarning 
              ? 'bg-yellow-500/20 border-yellow-500/30' 
              : 'bg-destructive/20 border-destructive/30'
          }`}>
            <Icon className={`w-8 h-8 ${
              isWarning ? 'text-yellow-500' : 'text-destructive'
            }`} />
          </div>
          <DialogTitle className="font-medieval text-xl text-parchment text-center">
            {config.title}
          </DialogTitle>
          <DialogDescription className="text-center font-body text-muted-foreground pt-2">
            {error.message}
          </DialogDescription>
        </DialogHeader>
        
        {error.warnings && error.warnings.length > 0 && (
          <Alert className="bg-yellow-500/10 border-yellow-500/30">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            <AlertDescription className="font-body text-sm">
              <ul className="list-disc list-inside space-y-1">
                {error.warnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}
        
        <div className="flex justify-center mt-4">
          <Button variant="gold" onClick={onClose}>
            {isWarning ? '계속하기' : '다시 시도하기'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ValidationErrorDialog;
export type { ValidationError };
