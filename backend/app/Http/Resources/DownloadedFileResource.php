<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class DownloadedFileResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->resource->id,
            'file_id' => $this->resource->file_id,
            'url' => $this->resource->url,
            'filename' => $this->resource->filename,
            'file_hash' => $this->resource->file_hash,
            'status_id' => $this->resource->status_id,
            'downloaded_at' => $this->resource->downloaded_at,
            'parsed_at' => $this->resource->parsed_at,
            'format' => $this->resource->format,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'status' => new EtlStatusResource($this->whenLoaded('status')),
            'logs' => EtlLogResource::collection($this->whenLoaded('logs')),
        ];
    }
}
