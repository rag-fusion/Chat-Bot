import { File, FileAudio, FileImage, FileText } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

function ResultScore({ score }) {
  return (
    <div className="flex items-center gap-1 text-xs">
      <span className="font-medium">Similarity:</span>
      <span
        className={`font-mono ${
          score > 0.8
            ? "text-green-500"
            : score > 0.6
            ? "text-yellow-500"
            : "text-red-500"
        }`}
      >
        {Math.round(score * 100)}%
      </span>
    </div>
  );
}

function TextResult({ result, onOpen }) {
  return (
    <div
      className="group flex cursor-pointer gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-accent"
      onClick={() => onOpen(result)}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
        <FileText className="h-5 w-5 text-muted-foreground" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium">{result.file}</p>
          <ResultScore score={result.score} />
        </div>
        <p className="line-clamp-2 text-xs text-muted-foreground">
          {result.text}
        </p>
        <p className="text-xs text-muted-foreground/60">
          Page {result.page || 1}
        </p>
      </div>
    </div>
  );
}

function ImageResult({ result, onOpen }) {
  return (
    <div
      className="group relative cursor-pointer overflow-hidden rounded-lg border bg-card transition-colors hover:bg-accent"
      onClick={() => onOpen(result)}
    >
      <img
        src={result.url || result.path}
        alt={result.caption || "Retrieved image"}
        className="aspect-video w-full object-cover"
      />
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-3">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium text-white">
            {result.caption || result.file}
          </p>
          <ResultScore score={result.score} />
        </div>
      </div>
    </div>
  );
}

function AudioResult({ result, onOpen }) {
  return (
    <div
      className="group flex cursor-pointer gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-accent"
      onClick={() => onOpen(result)}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
        <FileAudio className="h-5 w-5 text-muted-foreground" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium">{result.file}</p>
          <ResultScore score={result.score} />
        </div>
        <p className="line-clamp-2 text-xs text-muted-foreground">
          {result.transcript}
        </p>
        <p className="text-xs text-muted-foreground/60">
          {result.duration
            ? `${Math.floor(result.duration / 60)}:${String(
                Math.floor(result.duration % 60)
              ).padStart(2, "0")}`
            : "Unknown duration"}
        </p>
      </div>
    </div>
  );
}

export default function ContextViewer({ results, onOpen }) {
  // Filter results by type
  const textResults = results.filter(
    (r) => r.type === "text" || (!r.type && r.text)
  );
  const imageResults = results.filter(
    (r) => r.type === "image" || (!r.type && (r.url || r.path))
  );
  const audioResults = results.filter(
    (r) => r.type === "audio" || (!r.type && r.transcript)
  );

  return (
    <Tabs defaultValue="text" className="w-full">
      <TabsList className="w-full">
        <TabsTrigger value="text" className="flex-1">
          Text
          {textResults.length > 0 && (
            <span className="ml-1 text-xs">({textResults.length})</span>
          )}
        </TabsTrigger>
        <TabsTrigger value="images" className="flex-1">
          Images
          {imageResults.length > 0 && (
            <span className="ml-1 text-xs">({imageResults.length})</span>
          )}
        </TabsTrigger>
        <TabsTrigger value="audio" className="flex-1">
          Audio
          {audioResults.length > 0 && (
            <span className="ml-1 text-xs">({audioResults.length})</span>
          )}
        </TabsTrigger>
      </TabsList>

      <TabsContent value="text" className="mt-4 space-y-3">
        {textResults.length > 0 ? (
          textResults.map((result, idx) => (
            <TextResult key={idx} result={result} onOpen={onOpen} />
          ))
        ) : (
          <p className="text-center text-sm text-muted-foreground">
            No text results found
          </p>
        )}
      </TabsContent>

      <TabsContent value="images" className="mt-4 space-y-3">
        {imageResults.length > 0 ? (
          imageResults.map((result, idx) => (
            <ImageResult key={idx} result={result} onOpen={onOpen} />
          ))
        ) : (
          <p className="text-center text-sm text-muted-foreground">
            No image results found
          </p>
        )}
      </TabsContent>

      <TabsContent value="audio" className="mt-4 space-y-3">
        {audioResults.length > 0 ? (
          audioResults.map((result, idx) => (
            <AudioResult key={idx} result={result} onOpen={onOpen} />
          ))
        ) : (
          <p className="text-center text-sm text-muted-foreground">
            No audio results found
          </p>
        )}
      </TabsContent>
    </Tabs>
  );
}
