<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class SystemLogResource extends JsonResource
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
            'type' => $this->resource->type,
            'user_id' => $this->resource->user_id,
            'auditable_type' => $this->resource->auditable_type,
            'auditable_id' => $this->resource->auditable_id,
            'description' => $this->resource->description,
            'old_values' => $this->resource->old_values,
            'new_values' => $this->resource->new_values,
            'ip' => $this->resource->ip,
            'user_agent' => $this->resource->user_agent,
            'event' => $this->resource->event,
            'url' => $this->resource->url,
            'method' => $this->resource->method,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'user' => new UserResource($this->whenLoaded('user')),
        ];
    }
}
