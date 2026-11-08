<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
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
            'name' => $this->resource->name,
            'surname' => $this->resource->surname,
            'email' => $this->resource->email,
            'email_verified_at' => $this->resource->email_verified_at,
            'role_id' => $this->resource->role_id,
            'created_at' => $this->resource->created_at,
            'updated_at' => $this->resource->updated_at,
            'role' => new RoleResource($this->whenLoaded('role')),
        ];
    }
}
