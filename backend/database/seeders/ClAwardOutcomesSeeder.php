<?php

declare(strict_types=1);

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class ClAwardOutcomesSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('cl_award_outcomes')->insert([
            ['code' => 'selec-w', 'label_sk' => 'Víťaz vybraný'],
            ['code' => 'clos-nw', 'label_sk' => 'Uzavreté bez víťaza'],
            ['code' => 'open-nw', 'label_sk' => 'Otvorené, zatiaľ bez víťaza'],
        ]);
    }
}
