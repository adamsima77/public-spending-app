<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\SystemLog;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class SystemLogResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof SystemLog) {
            throw new UnexpectedValueException('SystemLogResource requires a SystemLog.');
        }

        return $this->resource->toArray();
    }
}
