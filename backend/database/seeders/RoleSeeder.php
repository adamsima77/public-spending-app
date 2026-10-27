<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $roles = ['Admin' => 'admin', 'Užívateľ' => 'user'];

        foreach ($roles as $role => $slug) {
            Role::create([
                'name' => $role,
                'slug' => $slug,
            ]);
        }
    }
}
