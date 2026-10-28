<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Notice;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class NoticeResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof Notice) {
            throw new UnexpectedValueException('NoticeResource requires a Notice.');
        }

        return $this->resource->toArray();
    }
}
