<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\SystemLog;
use App\Models\User;

class SystemLogPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin();
    }

    public function view(User $user, SystemLog $systemLog): bool
    {
        return $user->isAdmin();
    }
}
