import { useState, useRef } from "react";
import { Upload, Camera, X, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

interface ImageUploaderProps {
  onImageSelect: (file: File) => void;
  isLoading?: boolean;
}

const ImageUploader = ({ onImageSelect, isLoading = false }: ImageUploaderProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      onImageSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileChange(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const clearPreview = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
        className="hidden"
      />

      {!preview ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "relative aspect-[3/4] rounded-lg border-2 border-dashed cursor-pointer transition-all duration-300",
            "flex flex-col items-center justify-center gap-4 p-8",
            "gradient-card",
            isDragOver
              ? "border-gold shadow-gold scale-[1.02]"
              : "border-gold/40 hover:border-gold/60 hover:shadow-gold"
          )}
        >
          {/* Decorative corners */}
          <div className="absolute top-2 left-2 w-6 h-6 border-t-2 border-l-2 border-gold/50" />
          <div className="absolute top-2 right-2 w-6 h-6 border-t-2 border-r-2 border-gold/50" />
          <div className="absolute bottom-2 left-2 w-6 h-6 border-b-2 border-l-2 border-gold/50" />
          <div className="absolute bottom-2 right-2 w-6 h-6 border-b-2 border-r-2 border-gold/50" />

          <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center border border-gold/30">
            <Upload className="w-10 h-10 text-gold" />
          </div>
          
          <div className="text-center space-y-2">
            <p className="font-medieval text-lg text-parchment">
              전신 사진을 올려주세요
            </p>
            <p className="text-muted-foreground text-sm font-body">
              드래그 앤 드롭 또는 클릭하여 업로드
            </p>
          </div>

          <div className="flex gap-3 mt-2">
            <Button variant="dark" size="sm" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
              <Camera className="w-4 h-4 mr-2" />
              파일 선택
            </Button>
          </div>
        </div>
      ) : (
        <div className="relative aspect-[3/4] rounded-lg overflow-hidden border-ornate">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-full object-cover"
          />
          
          {isLoading && (
            <div className="absolute inset-0 bg-background/80 flex flex-col items-center justify-center gap-4">
              <Loader2 className="w-12 h-12 text-gold animate-spin" />
              <p className="font-medieval text-gold animate-pulse">
                캐릭터 생성 중...
              </p>
            </div>
          )}

          {!isLoading && (
            <button
              onClick={clearPreview}
              className="absolute top-3 right-3 w-8 h-8 rounded-full bg-background/80 flex items-center justify-center border border-gold/30 hover:bg-background transition-colors"
            >
              <X className="w-4 h-4 text-parchment" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
