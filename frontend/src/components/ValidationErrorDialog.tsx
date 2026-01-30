import { AlertTriangle, UserX, Footprints, Cat } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export type ValidationErrorType = "no_human" | "not_fullbody" | "animal_detected";

interface ValidationError {
  type: ValidationErrorType;
  message: string;
}

const errorConfig: Record<ValidationErrorType, { icon: React.ComponentType<{ className?: string }>; title: string }> = {
  no_human: {
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
};

interface ValidationErrorDialogProps {
  error: ValidationError | null;
  onClose: () => void;
}

const ValidationErrorDialog = ({ error, onClose }: ValidationErrorDialogProps) => {
  if (!error) return null;

  const config = errorConfig[error.type];
  const Icon = config.icon;

  return (
    <Dialog open={!!error} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md gradient-card border-gold/30">
        <DialogHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center border border-destructive/30">
            <Icon className="w-8 h-8 text-destructive" />
          </div>
          <DialogTitle className="font-medieval text-xl text-parchment text-center">
            {config.title}
          </DialogTitle>
          <DialogDescription className="text-center font-body text-muted-foreground pt-2">
            {error.message}
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex justify-center mt-4">
          <Button variant="gold" onClick={onClose}>
            다시 시도하기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ValidationErrorDialog;
export type { ValidationError };
