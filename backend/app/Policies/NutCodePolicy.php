<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\NutCode;
use App\Models\User;

class NutCodePolicy
{
    public function create(User $user): bool
    {
        return $user->isAdmin();
    }

    public function update(User $user, NutCode $nutCode): bool
    {
        return $user->isAdmin();
    }

    public function destroy(User $user, NutCode $nutCode): bool
    {
        return $user->isAdmin();
    }
}
