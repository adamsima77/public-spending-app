<?php

declare(strict_types=1);

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class ClCompanySizesSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('cl_company_sizes')->insert([
            ['code' => 'micro', 'label_sk' => 'Mikropodnik'],
            ['code' => 'small', 'label_sk' => 'Malý podnik'],
            ['code' => 'medium', 'label_sk' => 'Stredný podnik'],
            ['code' => 'large', 'label_sk' => 'Veľký podnik'],
        ]);
    }
}
