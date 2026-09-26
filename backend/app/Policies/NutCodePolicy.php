<?php

namespace App\Policies;

use App\Models\User;
use App\Models\NutCode;

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
