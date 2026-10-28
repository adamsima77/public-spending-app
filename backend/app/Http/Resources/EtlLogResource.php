<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\EtlLog;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class EtlLogResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof EtlLog) {
            throw new UnexpectedValueException('EtlLogResource requires an EtlLog.');
        }

        return $this->resource->toArray();
    }
}
