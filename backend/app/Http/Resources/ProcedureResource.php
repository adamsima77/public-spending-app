<?php

declare(strict_types=1);

namespace App\Http\Resources;

use App\Models\Procedure;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use UnexpectedValueException;

class ProcedureResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        if (! $this->resource instanceof Procedure) {
            throw new UnexpectedValueException('ProcedureResource requires a Procedure.');
        }

        return $this->resource->toArray();
    }
}
