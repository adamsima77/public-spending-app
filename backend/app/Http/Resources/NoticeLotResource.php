<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\NoticeLot;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class NoticeLotResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof NoticeLot) {
            throw new UnexpectedValueException('NoticeLotResource requires a NoticeLot.');
        }

        return $this->resource->toArray();
    }
}
