<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\Role;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $roles = ['Admin' => 'admin', 'Užívateľ' => 'user'];

        foreach($roles as $role => $slug)
        {
            Role::create([
                'name' => $role,
                'slug' => $slug
            ]);    
        }    
    }
}
