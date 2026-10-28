<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\DownloadedFile;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class DownloadedFileResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof DownloadedFile) {
            throw new UnexpectedValueException('DownloadedFileResource requires a DownloadedFile.');
        }

        return $this->resource->toArray();
    }
}
