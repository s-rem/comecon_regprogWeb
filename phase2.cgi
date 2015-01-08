#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use SFCON::Register;

#定数定義
require('pgreglib.pl');
our %CONDEF_CONST;

my $register = SFCON::Register->new;
my $cgi = CGI->new;

# セッションID = urlパラメータ||cookieからCGISESSID||取得できなかったらundef．
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});
my $input_page;
my $http_header;

if(defined $sid && $sid eq $session->id){
    # 取得したセッションidが有効:確認画面表示
    $input_page=HTML::Template->new(filename => 'phase2-tmpl.html');
	$input_page->param(ID => $session->id);
	$session->param('phase', '2-1');

    # テンプレートにパラメータを設定
    html_out_simple($input_page, $session);
    html_out_table($input_page, $session);
    html_out_guest($input_page, $session);

	$http_header = $cgi->header(-charset=>'UTF-8', -expires=>'now');
} else{
    # 古いセッションを削除
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
    # 取得したセッションidが無効:エラー画面表示
    $input_page=HTML::Template->new(filename => 'error.html');
	$http_header = $cgi->header(-charset=>'UTF-8');
}
# 共通のTMPL変数置き換え
$input_page->param(ID => $sid);
$input_page->param(CONNAME   => $CONDEF_CONST{'CONNAME'});
$input_page->param(FULLNAME  => $CONDEF_CONST{'FULLNAME'});
$input_page->param(CONPERIOD => $CONDEF_CONST{'CONPERIOD'});

print $http_header;
print "\n\n";
print $input_page->output;

exit;

# 単純置き換え
sub html_out_simple {
    my (
        $page,  # HTML::Templateオブジェクト
        $sprm,  # CGI::Sessionオブジェクト
    ) = @_;
    # 単純置き換え パラメータ名配列
    my @org_pname = (
        "p1_name", "email", "reg_num", "tel", "fax", "cellphone",
        "pg_name", "pg_name_f", "pg_naiyou", "fc_other_naiyou",
        "fc_mochikomi", "pg_badprog",
        "fc_comment",
    );
    # 単純置き換え
    foreach my $pname ( @org_pname ) {
        my $value = $sprm->param($pname);
        $value =~ s/[\r\n]+/<br\/>/mg;
	    $page->param( $pname => $value );
    }
}

# テーブル定義変換
sub html_out_table {
    my (
        $page,  # HTML::Templateオブジェクト
        $sprm,  # CGI::Sessionオブジェクト
    ) = @_;

    # テーブル変換 パラメータテーブル
    #   key: パラメータ名
    #   value[0]:変換テーブル
    #   value[1]:その他内容パラメータ名
    my %tbl_pname = (
        "pg_kind"   =>      # 企画種別table
            [   {
                "K-A1"  => "講演",
                "K-A2"  => "パネルディスカッション",
                "K-A3"  => "講座",
                "K-A4"  => "上映",
                "K-A5"  => "座談会",
                "K-A6"  => "お茶会",
                "K-A7"  => "ゲーム",
                "K-B1"  => "コンサート",
                "K-C1"  => "展示",
                "K-D1"  => "印刷物発行",
                "K-E1"  => "投票",
                "K-X1"  => "その他",
                },
                "pg_kind2",
            ],
        "pg_place"  =>      # 希望場所table
            [   {
                "P-N"   => "特になし",
                "P-C1"  => "会議室",
                "P-H1"  => "小ホール(300人)",
                "P-X1"  => "その他",
                },
                "pg_place2",
            ],
        "pg_layout"   =>    # レイアウトtable
            [   {
                "0" => "シアター",
                "1" => "スクール",
                "2" => "ロの字",
                "3" => "島組",
                "9" => "その他",
                },
                "pg_layout2",
            ],
        "pg_time"   =>      # 希望日時table
            [   {
                "T-N"       => "特になし",
                "T-1any"    => "29日(土)のどこでも",
                "T-1am"     => "29日(土)午前",
                "T-1pm"     => "29日(土)午後",
                "T-1ngt"    => "29日(土)夜(パーティ後)",
                "T-2any"    => "30日(日)のどこでも",
                "T-2am"     => "30日(日)午前",
                "T-2pm"     => "30日(日)午後",
                "T-wday"    => "両日",
                "T-X1"      => "その他",
                },
                "pg_time2",
            ],
        "pg_koma"   =>      # 希望コマ数table
            [   {
                "TK-1"  => "１コマ(90分+準備30分)",
                "TK-2"  => "２コマ(210分+準備30分)",
                "TK-A"  => "終日",
                "TK-X1" => "その他",
                },
                "pg_koma2",
            ],
        "pg_ninzu"  =>      # 予想参加者table
            [   {
                "TN-0"  => "不明",
                "TN-1"  => "20人まで",
                "TN-2"  => "50人まで",
                "TN-3"  => "100人まで",
                "TN-4"  => "200人まで",
                "TN-5"  => "200人超",
                },
                undef,
            ],
        "pg_naiyou_k"   =>  # 内容事前公開table
            [   {
                "CX-0"  => "事前公開可",
                "CX-1"  => "事前公開不可",
                },
                undef,
            ],
        "pg_kiroku_kb"  =>  # リアルタイム公開table
            [   {
                "CX-0"  => "UST等動画を含む全て許可",
                "CX-1"  => "twitter等テキストと静止画公開可",
                "CX-2"  => "テキストのみ公開可",
                "CX-3"  => "公開不可",
                "CX-9"  => "その他",
                },
                undef,
            ],
        "pg_kiroku_ka"  =>  # 事後公開table
            [   {
                "CX-0"  => "UST等動画を含む全て許可",
                "CX-1"  => "blog等テキストと静止画公開可",
                "CX-2"  => "テキストのみ公開可",
                "CX-3"  => "公開不可",
                "CX-9"  => "その他",
                },
                undef,
            ],
        "pg_enquete"    =>  # 企画経験table
            [   {
                "0" => "初めて",
                "1" => "昨年に続いて2回目",
                "2" => "継続して3〜5回目",
                "3" => "ひさしぶり",
                "4" => "6回目以上",
                },
                undef,
            ],
    );
    # 使用する/しない パラメータテーブル
    #   key: パラメータ名
    #   value: 本数パラメータ名
    my %useunuse_pname = (
        "wbd"   =>  undef,
        "mic"   =>  "miccnt",
        "mic2"  =>  "mic2cnt",
        "mon"   =>  undef,
        "dvd"   =>  undef,
        "bdp"   =>  undef,
        "syo"   =>  undef,
    );

    # 持ち込む/持ち込まない パラメータテーブル
    #   key: パラメータ名
    #   value: パラメータテーブル
    #       key:パラメータ名
    #       value[0]:変換テーブル
    #       value[1]:その他内容パラメータ名
    #       value[2]:注釈
    my %motikomi_pname = (
        "fc_vid"    => {
            "av-v"  =>      # 持ち込み映像機器映像接続形式",
                [   {
                    "hdmi"      => "HDMI",
                    "svideo"    => "S-Video",
                    "rca"       => "RCAコンポジット(黄)",
                    "other"     => "その他",
                    },
                    "av-v_velse",
                    "映像接続",
                ],
            "av-a"  =>      # 持ち込み映像機器音声接続形式
                [   {
                    "none"  => "不要",
                    "tsr"   => "ステレオミニ(3.5mmTSR)",
                    "rca"   => "RCAコンポジット(赤白)",
                    "other" => "その他",
                    },
                    "av-a_velse",
                    "音声接続",
                ],
        },
        "fc_pc"     => {
            "pc-v"  =>      # 持ち込みPC映像接続形式
                [   {
                    "none"  => "接続しない",
                    "hdmi"  => "HDMI",
                    "vga"   => "D-Sub15(VGA)",
                    "other" => "その他",
                    },
                    "pc-v_velse",
                    "映像接続",
                ],
            "pc-a"  =>      # 持ち込みPC音声接続形式
                [   {
                    "none"      => "不要",
                    "svideo"    => "ステレオミニ(3.5mmTSR)",
                    "rca"       => "RCAコンポジット(赤白)",
                    "other"     => "その他",
                    },
                    "pc-a_velse",
                    "音声接続",
                ],
        },
    );

    # ネット接続テーブル変換 パラメータテーブル
    #   PC持ち込み時のみ変換するため、別テーブルとする
    #   key: パラメータ名
    #   value[0]:変換テーブル
    #   value[1]:その他内容パラメータ名
    my %lan_pname = (
        "lan"   =>
            [   {
                "none"  => "接続しない",
                "lan"   => "有線(RJ-45)",
                "wifi"  => "無線",
                "other" => "その他",
                },
                "pc-l_velse",
            ],
    );

    my %motikomi_tbl = (   # 持ち込む/持ち込まないtable
        "0" => "持ち込む",
        "1" => "持ち込まない",
    );

    my $pname;
    my $pAprm;

    # テーブル変換(その他解釈込み)
    while ( ($pname, $pAprm) = each %tbl_pname ) {
        $page->param( $pname => cnv_radio_val($sprm, $pname, $pAprm ));
    }
    # 使用する/しない(本数解釈込み)
    while ( ($pname, $pAprm) = each %useunuse_pname ) {
	    $page->param( $pname => cnv_useunuse_val($sprm, $pname, $pAprm));
    }
    # 持ち込む/持ち込まない(追加項目解釈込み)
    while ( ($pname, $pAprm) = each %motikomi_pname ) {
        my $value = $motikomi_tbl{$sprm->param($pname)};
        if ( $value eq "持ち込む" ) {
            while ( my ($pn2, $pAp2) = each %$pAprm ) {
                $value .= '<div class="indent">'
                        . $pAp2->[2] . ':'
                        . cnv_radio_val($sprm, $pn2, $pAp2)
                        . '</div>'
            }
        }
	    $page->param( $pname => $value );
    }
    # ネット接続に関する特殊処理
    if ( $motikomi_tbl{$sprm->param("fc_pc")} eq "持ち込む" ) {
        while ( ($pname, $pAprm) = each %lan_pname ) {
            my $value = cnv_radio_val($sprm, $pname, $pAprm);
            if ( $value ne "接続しない" ) {
                $value .= '<br/><b>利用方法</b>'
                        . '<div class="indent">'
                        . $sprm->param("lanreason")
                        . '</div>';
            }
            $value =~ s/[\r\n]+/<br\/>/mg;
            $page->param( $pname => $value );
        }
    }
}

# テーブル変換(その他解釈込み)
sub cnv_radio_val {
    my (
        $sprm,      # CGI::Sessionオブジェクト
        $pname,     # パラメータ名
        $pAprm,     # 追加情報 [0]:変換テーブル [1]:その他内容パラメータ名
    ) = @_;

    my $value = $pAprm->[0]->{$sprm->param($pname)};
    if ( ( $pAprm->[1] ne undef ) and ( $value eq "その他" ) ) {
        $value .= '(' . $sprm->param($pAprm->[1]) . ')';
    }
    return ($value);
}

# 使用する/しない(本数解釈込み)
sub cnv_useunuse_val {
    my (
        $sprm,      # CGI::Sessionオブジェクト
        $pname,     # パラメータ名
        $opname,    # 追加情報パラメータ名 undef:なし
    ) = @_;

    my $value = $sprm->param($pname) ? "使用する" : "使用しない";
    if ( $opname && ( $value eq "使用する" ) ) {
        $value .= ' (' . $sprm->param($opname) . '本)';
    }
    return ($value);
}

# 出演者情報(LOOP)
sub html_out_guest{
    my (
        $page,  # HTML::Templateオブジェクト
        $sprm,  # CGI::Sessionオブジェクト
    ) = @_;

    my %ppn_youdo_tbl = (   # 自身出演table
        "0" => "する",
        "1" => "しない",
    );

    my %ppn_con_tbl = (     # 出演交渉table
        "PP-A"  => "交渉を大会に依頼",
        "PP-B1" => "出演了承済",
        "PP-B2" => "交渉中",
        "PP-B3" => "未交渉",
    );

    my %ppn_grq_tbl = (     # ゲスト申請table
        "PP-A"  => "する",
        "PP-B"  => "しない",
    );

    $page->param( "youdo" => $ppn_youdo_tbl{$sprm->param("youdo")} );
    my @loop_data = ();  # TMPL変数名=>値ハッシュ参照 の配列
    my $ppcnt;
	for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {	# CONST: 出演者の最大値
        my $prefix = 'pp' . $ppcnt;
		my $ppname = $sprm->param($prefix . '_name');
        if ( $ppname  ne '') {
            my %row_data;
            $row_data{"pp_number"}  = $ppcnt;
            $row_data{"pp_name"}    = $ppname;
			$row_data{"pp_name_f"}  = $sprm->param($prefix . '_name_f');
            $row_data{"pp_con"} = $ppn_con_tbl{$sprm->param($prefix . '_con')};
            $row_data{"pp_grq"} = $ppn_grq_tbl{$sprm->param($prefix . '_grq')};
            push(@loop_data, \%row_data);
		}
	}
    $page->param(GUEST_LOOP => \@loop_data);
}

1;
#end
