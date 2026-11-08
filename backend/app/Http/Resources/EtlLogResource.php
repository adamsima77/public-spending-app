<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EtlLogResource extends JsonResource
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
            'level' => $this->resource->level,
            'message' => $this->resource->message,
            'context' => $this->resource->context,
            'created_at' => $this->resource->created_at,
            'file' => new DownloadedFileResource($this->whenLoaded('file')),
        ];
    }
}
