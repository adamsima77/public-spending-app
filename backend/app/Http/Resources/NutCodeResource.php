<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\NutCode;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class NutCodeResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof NutCode) {
            throw new UnexpectedValueException('NutCodeResource requires a NutCode.');
        }

        return $this->resource->toArray();
    }
}
